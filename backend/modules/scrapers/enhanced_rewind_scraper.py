##########################
### Import Statements ####
##########################

# local imports
from . import update_sys_path
update_sys_path()

import time
import asyncio
import threading
from datetime import datetime, timedelta
from collections import deque
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Import existing scraper
from .rewind_lol_scraper import LeagueChampScraper
import modules.utils.color_utils as ColorPrint

# Selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

##########################
### Enhanced Classes #####
##########################

class ProfileStatus(Enum):
    """Profile status enumeration"""
    EXISTS = "exists"
    NEEDS_CREATION = "needs_creation"
    UPDATING = "updating"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"

@dataclass
class UpdateRequest:
    """Data class for tracking update requests"""
    riot_id: str
    request_time: datetime
    status: ProfileStatus
    attempt_count: int = 0
    
class RateLimitManager:
    """
    [info] Manages dual rate limiting for rewind.lol
    
    Tracks both concurrent request limits (5 max) and time-window limits
    to prevent reCAPTCHA triggers and queue overflow errors.
    """
    
    def __init__(self, concurrent_limit: int = 5, time_window_minutes: int = 5):
        self.concurrent_limit = concurrent_limit
        self.time_window = timedelta(minutes=time_window_minutes)
        self.active_requests: Dict[str, UpdateRequest] = {}
        self.request_history: deque = deque()
        self.last_captcha_time: Optional[datetime] = None
        self.adaptive_delay = 30  # Start with 30 second delays
        
    def can_make_request(self) -> Tuple[bool, str]:
        """
        [info] Checks if a new request can be made based on rate limits
        
        [return] Tuple[bool, str]: (can_make_request, reason_if_not)
        """
        # Check concurrent limit
        if len(self.active_requests) >= self.concurrent_limit:
            return False, f"Concurrent limit reached ({len(self.active_requests)}/{self.concurrent_limit})"
        
        # Check time window limit
        current_time = datetime.now()
        cutoff_time = current_time - self.time_window
        
        # Clean old requests from history
        while self.request_history and self.request_history[0] < cutoff_time:
            self.request_history.popleft()
        
        # If we had a recent captcha, be extra careful
        if self.last_captcha_time and (current_time - self.last_captcha_time) < timedelta(minutes=10):
            if len(self.request_history) >= 2:  # Very conservative after captcha
                return False, "Post-captcha cooldown active"
        
        # Adaptive limit based on request history
        max_requests_in_window = max(1, 5 - len(self.request_history))
        if len(self.request_history) >= max_requests_in_window:
            return False, f"Time window limit reached ({len(self.request_history)}/{max_requests_in_window})"
        
        return True, "OK"
    
    def register_request(self, riot_id: str) -> UpdateRequest:
        """
        [info] Registers a new request and adds to tracking
        
        [param] riot_id: str - Riot ID being processed
        [return] UpdateRequest: The created request object
        """
        current_time = datetime.now()
        request = UpdateRequest(riot_id, current_time, ProfileStatus.UPDATING)
        
        self.active_requests[riot_id] = request
        self.request_history.append(current_time)
        
        print(f"{ColorPrint.CYAN}[Rate Limit] Registered request for {riot_id} "
              f"({len(self.active_requests)}/{self.concurrent_limit} active){ColorPrint.RESET}")
        
        return request
    
    def complete_request(self, riot_id: str, success: bool = True):
        """
        [info] Marks a request as complete and removes from active tracking
        
        [param] riot_id: str - Riot ID that completed
        [param] success: bool - Whether the request succeeded
        """
        if riot_id in self.active_requests:
            request = self.active_requests.pop(riot_id)
            status = "SUCCESS" if success else "FAILED"
            print(f"{ColorPrint.CYAN}[Rate Limit] Completed request for {riot_id} ({status}) "
                  f"({len(self.active_requests)}/{self.concurrent_limit} active){ColorPrint.RESET}")
    
    def register_captcha(self):
        """
        [info] Registers that a captcha was encountered, adjusting future limits
        """
        self.last_captcha_time = datetime.now()
        self.adaptive_delay = min(120, self.adaptive_delay * 1.5)  # Increase delay, max 2 minutes
        print(f"{ColorPrint.RED}[Rate Limit] CAPTCHA encountered! Increasing delays to {self.adaptive_delay}s{ColorPrint.RESET}")
    
    def get_recommended_delay(self) -> int:
        """
        [info] Returns recommended delay before next request
        
        [return] int: Delay in seconds
        """
        if self.last_captcha_time and (datetime.now() - self.last_captcha_time) < timedelta(minutes=10):
            return self.adaptive_delay
        
        # Base delay increases with request frequency
        base_delay = 15 + (len(self.request_history) * 5)
        return min(60, base_delay)  # Max 1 minute delay

class ProfileManager:
    """
    [info] Manages profile detection, creation, and updates on rewind.lol
    
    Handles the complete workflow from profile detection through creation/update
    to completion monitoring.
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.base_url = "https://rewind.lol/"
        
        # XPath constants based on your specifications
        self.SEARCH_INPUT_XPATH = "/html/body/main/div/div/div/form/div/input"
        self.REGION_SELECT_XPATH = "/html/body/main/div/div/div/form/div/div[2]/select"
        self.NA_OPTION_XPATH = "/html/body/main/div/div/div/form/div/div[2]/select/option[8]"
        self.SEARCH_BUTTON_XPATH = "/html/body/main/div/div/div/form/div/button"
        self.UPDATE_BUTTON_XPATH = "/html/body/div[1]/div/form/button"
        self.CREATE_BUTTON_XPATH = "/html/body/main/div/div/div/div/form/div/button"
        
        # Text patterns for detection
        self.PROFILE_CREATION_TEXT = "A profile needs to be created for"
        self.QUEUE_ERROR_TEXT = "The summoner you specified could not be added to the queue"
        self.TOO_MANY_REQUESTS_TEXT = "Too many requests in the queue from this IP Address"
    
    def navigate_to_home(self):
        """
        [info] Navigates to rewind.lol homepage
        """
        print(f"{ColorPrint.YELLOW}>> Navigating to {self.base_url}{ColorPrint.RESET}")
        self.driver.get(self.base_url)
        time.sleep(2)
    
    def search_profile(self, riot_id: str) -> ProfileStatus:
        """
        [info] Searches for a profile and determines its status
        
        [param] riot_id: str - Riot ID to search for
        [return] ProfileStatus: Current status of the profile
        """
        try:
            print(f"{ColorPrint.CYAN}[Profile Search] Searching for {riot_id}{ColorPrint.RESET}")
            
            # Navigate to home page
            self.navigate_to_home()
            
            # Enter riot ID in search box
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.SEARCH_INPUT_XPATH))
            )
            search_input.clear()
            search_input.send_keys(riot_id)
            
            # Select NA region
            region_select = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.REGION_SELECT_XPATH))
            )
            region_select.click()
            
            na_option = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, self.NA_OPTION_XPATH))
            )
            na_option.click()
            
            # Click search button
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.SEARCH_BUTTON_XPATH))
            )
            search_button.click()
            
            # Wait for page to load and check result
            time.sleep(3)
            
            page_source = self.driver.page_source
            
            # Check for profile creation needed
            if self.PROFILE_CREATION_TEXT in page_source:
                print(f"{ColorPrint.YELLOW}[Profile Search] Profile needs creation for {riot_id}{ColorPrint.RESET}")
                return ProfileStatus.NEEDS_CREATION
            
            # Check for rate limiting errors
            if self.QUEUE_ERROR_TEXT in page_source or self.TOO_MANY_REQUESTS_TEXT in page_source:
                print(f"{ColorPrint.RED}[Profile Search] Rate limited for {riot_id}{ColorPrint.RESET}")
                return ProfileStatus.RATE_LIMITED
            
            # Check for reCAPTCHA
            if "recaptcha" in page_source.lower():
                print(f"{ColorPrint.RED}[Profile Search] reCAPTCHA triggered for {riot_id}{ColorPrint.RESET}")
                return ProfileStatus.RATE_LIMITED
            
            # If we're on a profile page, profile exists
            if "user_champions" in self.driver.current_url or "Champions Played" in page_source:
                print(f"{ColorPrint.GREEN}[Profile Search] Profile exists for {riot_id}{ColorPrint.RESET}")
                return ProfileStatus.EXISTS
            
            print(f"{ColorPrint.RED}[Profile Search] Unknown status for {riot_id}{ColorPrint.RESET}")
            return ProfileStatus.ERROR
            
        except Exception as e:
            print(f"{ColorPrint.RED}[Profile Search] Error searching for {riot_id}: {e}{ColorPrint.RESET}")
            return ProfileStatus.ERROR
    
    def create_profile(self, riot_id: str) -> bool:
        """
        [info] Creates a new profile (assumes we're on the creation page)
        
        [param] riot_id: str - Riot ID to create profile for
        [return] bool: True if creation initiated successfully
        """
        try:
            print(f"{ColorPrint.CYAN}[Profile Creation] Creating profile for {riot_id}{ColorPrint.RESET}")
            
            # Find and click create button
            create_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.CREATE_BUTTON_XPATH))
            )
            create_button.click()
            
            # Check for immediate errors
            time.sleep(2)
            page_source = self.driver.page_source
            
            if "recaptcha" in page_source.lower():
                print(f"{ColorPrint.RED}[Profile Creation] reCAPTCHA triggered during creation{ColorPrint.RESET}")
                return False
            
            if self.QUEUE_ERROR_TEXT in page_source or self.TOO_MANY_REQUESTS_TEXT in page_source:
                print(f"{ColorPrint.RED}[Profile Creation] Rate limited during creation{ColorPrint.RESET}")
                return False
            
            print(f"{ColorPrint.GREEN}[Profile Creation] Creation initiated for {riot_id}{ColorPrint.RESET}")
            return True
            
        except Exception as e:
            print(f"{ColorPrint.RED}[Profile Creation] Error creating profile for {riot_id}: {e}{ColorPrint.RESET}")
            return False
    
    def trigger_update(self, riot_id: str) -> bool:
        """
        [info] Triggers an update for existing profile (assumes we're on profile page)
        
        [param] riot_id: str - Riot ID to update
        [return] bool: True if update initiated successfully
        """
        try:
            print(f"{ColorPrint.CYAN}[Profile Update] Triggering update for {riot_id}{ColorPrint.RESET}")
            
            # Find and click update button
            update_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.UPDATE_BUTTON_XPATH))
            )
            update_button.click()
            
            # Check for immediate errors
            time.sleep(2)
            page_source = self.driver.page_source
            
            if "recaptcha" in page_source.lower():
                print(f"{ColorPrint.RED}[Profile Update] reCAPTCHA triggered during update{ColorPrint.RESET}")
                return False
            
            if self.QUEUE_ERROR_TEXT in page_source or self.TOO_MANY_REQUESTS_TEXT in page_source:
                print(f"{ColorPrint.RED}[Profile Update] Rate limited during update{ColorPrint.RESET}")
                return False
            
            print(f"{ColorPrint.GREEN}[Profile Update] Update initiated for {riot_id}{ColorPrint.RESET}")
            return True
            
        except Exception as e:
            print(f"{ColorPrint.RED}[Profile Update] Error updating profile for {riot_id}: {e}{ColorPrint.RESET}")
            return False
    
    def wait_for_completion(self, riot_id: str, timeout_minutes: int = 5) -> bool:
        """
        [info] Waits for profile creation/update to complete
        
        [param] riot_id: str - Riot ID being processed
        [param] timeout_minutes: int - Maximum time to wait
        [return] bool: True if completed successfully
        """
        print(f"{ColorPrint.YELLOW}[Profile Wait] Waiting for completion of {riot_id}{ColorPrint.RESET}")
        
        start_time = time.time()
        max_wait = timeout_minutes * 60
        
        while (time.time() - start_time) < max_wait:
            try:
                # Check if we're redirected to profile page
                current_url = self.driver.current_url
                
                if "user_champions" in current_url or riot_id.replace("#", "-").lower() in current_url.lower():
                    print(f"{ColorPrint.GREEN}[Profile Wait] {riot_id} completed successfully{ColorPrint.RESET}")
                    return True
                
                # Check for error conditions
                page_source = self.driver.page_source
                if "error" in page_source.lower() or "failed" in page_source.lower():
                    print(f"{ColorPrint.RED}[Profile Wait] Error detected for {riot_id}{ColorPrint.RESET}")
                    return False
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"{ColorPrint.RED}[Profile Wait] Error waiting for {riot_id}: {e}{ColorPrint.RESET}")
                time.sleep(5)
        
        print(f"{ColorPrint.RED}[Profile Wait] Timeout waiting for {riot_id}{ColorPrint.RESET}")
        return False

class ConcurrentUpdateManager:
    """
    [info] Manages concurrent profile updates with proper rate limiting
    
    Orchestrates the entire process of checking, creating, and updating profiles
    while respecting both concurrent and time-window rate limits.
    """
    
    def __init__(self, driver):
        self.driver = driver
        self.rate_limiter = RateLimitManager()
        self.profile_manager = ProfileManager(driver)
        self.update_queue: List[str] = []
        self.completed_profiles: List[str] = []
        self.failed_profiles: List[str] = []
    
    def process_profiles_batch(self, riot_ids: List[str]) -> Dict[str, str]:
        """
        [info] Processes a batch of profiles with smart rate limiting
        
        [param] riot_ids: List[str] - List of Riot IDs to process
        [return] Dict[str, str]: Results mapping riot_id -> status
        """
        results = {}
        remaining_profiles = riot_ids.copy()
        
        print(f"{ColorPrint.MAGENTA}[Batch Process] Starting batch of {len(riot_ids)} profiles{ColorPrint.RESET}")
        
        while remaining_profiles:
            # Check if we can make a request
            can_request, reason = self.rate_limiter.can_make_request()
            
            if not can_request:
                delay = self.rate_limiter.get_recommended_delay()
                print(f"{ColorPrint.YELLOW}[Batch Process] Rate limited: {reason}. Waiting {delay}s{ColorPrint.RESET}")
                time.sleep(delay)
                continue
            
            # Process next profile
            riot_id = remaining_profiles.pop(0)
            result = self._process_single_profile(riot_id)
            results[riot_id] = result
            
            # Add delay between requests
            if remaining_profiles:  # Don't delay after last profile
                delay = self.rate_limiter.get_recommended_delay()
                print(f"{ColorPrint.CYAN}[Batch Process] Waiting {delay}s before next profile{ColorPrint.RESET}")
                time.sleep(delay)
        
        print(f"{ColorPrint.MAGENTA}[Batch Process] Completed batch. "
              f"Success: {sum(1 for v in results.values() if v == 'success')}, "
              f"Failed: {sum(1 for v in results.values() if v != 'success')}{ColorPrint.RESET}")
        
        return results
    
    def _process_single_profile(self, riot_id: str) -> str:
        """
        [info] Processes a single profile through the complete workflow
        
        [param] riot_id: str - Riot ID to process
        [return] str: Result status
        """
        try:
            # Register the request
            request = self.rate_limiter.register_request(riot_id)
            
            # Step 1: Check profile status
            status = self.profile_manager.search_profile(riot_id)
            
            if status == ProfileStatus.RATE_LIMITED:
                self.rate_limiter.register_captcha()
                self.rate_limiter.complete_request(riot_id, False)
                return "rate_limited"
            
            elif status == ProfileStatus.ERROR:
                self.rate_limiter.complete_request(riot_id, False)
                return "error"
            
            # Step 2: Handle profile creation or update
            success = False
            
            if status == ProfileStatus.NEEDS_CREATION:
                success = self.profile_manager.create_profile(riot_id)
            elif status == ProfileStatus.EXISTS:
                success = self.profile_manager.trigger_update(riot_id)
            
            if not success:
                if "recaptcha" in self.driver.page_source.lower():
                    self.rate_limiter.register_captcha()
                self.rate_limiter.complete_request(riot_id, False)
                return "failed_to_initiate"
            
            # Step 3: Wait for completion
            completed = self.profile_manager.wait_for_completion(riot_id)
            
            self.rate_limiter.complete_request(riot_id, completed)
            
            if completed:
                self.completed_profiles.append(riot_id)
                return "success"
            else:
                self.failed_profiles.append(riot_id)
                return "timeout"
                
        except Exception as e:
            print(f"{ColorPrint.RED}[Single Process] Error processing {riot_id}: {e}{ColorPrint.RESET}")
            self.rate_limiter.complete_request(riot_id, False)
            return "exception"

##################################
### Enhanced LeagueChampScraper ###
##################################

class EnhancedLeagueChampScraper(LeagueChampScraper):
    """
    [info] Enhanced version of LeagueChampScraper with auto-creation and update capabilities
    
    Extends the base LeagueChampScraper with intelligent profile management,
    rate limiting, and concurrent update handling.
    """
    
    @staticmethod
    def auto_update_team_champ_history(tournament_id: str, team_id: str, player_riot_ids: list, 
                                     run_update: bool = True, max_retries: int = 2):
        """
        [info] Enhanced version with auto-creation and intelligent rate limiting
        
        [param] tournament_id: str - Tournament identifier
        [param] team_id: str - Team identifier
        [param] player_riot_ids: list - List of player Riot IDs to process
        [param] run_update: bool - Whether to actually run updates (default: True)
        [param] max_retries: int - Maximum retries for failed profiles
        """
        if not run_update:
            print(f"{ColorPrint.YELLOW}[Auto Update] Update disabled, skipping{ColorPrint.RESET}")
            return
        
        # Setup the rewind.lol website for scraping
        EnhancedLeagueChampScraper.set_up_rewind_lol()
        
        # Flatten and clean profile list
        profiles_to_process = []
        for player_account in player_riot_ids:
            if not player_account:
                continue
                
            if isinstance(player_account, str):
                if '#' in player_account:
                    profiles_to_process.append(player_account)
            elif isinstance(player_account, list):
                for account in player_account:
                    if isinstance(account, str) and '#' in account:
                        profiles_to_process.append(account)
        
        if not profiles_to_process:
            print(f"{ColorPrint.RED}[Auto Update] No valid profiles found{ColorPrint.RESET}")
            return
        
        print(f"{ColorPrint.MAGENTA}[Auto Update] Processing {len(profiles_to_process)} profiles for {team_id}{ColorPrint.RESET}")
        
        # Initialize concurrent manager
        update_manager = ConcurrentUpdateManager(EnhancedLeagueChampScraper.DRIVER)
        
        # Process all profiles
        results = update_manager.process_profiles_batch(profiles_to_process)
        
        # Handle retries for failed profiles
        failed_profiles = [rid for rid, status in results.items() if status not in ['success']]
        
        for retry_attempt in range(max_retries):
            if not failed_profiles:
                break
                
            print(f"{ColorPrint.YELLOW}[Auto Update] Retry {retry_attempt + 1}/{max_retries} for {len(failed_profiles)} failed profiles{ColorPrint.RESET}")
            time.sleep(60)  # Wait longer between retries
            
            retry_results = update_manager.process_profiles_batch(failed_profiles)
            
            # Update results and failed list
            results.update(retry_results)
            failed_profiles = [rid for rid, status in retry_results.items() if status not in ['success']]
        
        # Report final results
        successful = [rid for rid, status in results.items() if status == 'success']
        final_failed = [rid for rid, status in results.items() if status not in ['success']]
        
        print(f"{ColorPrint.GREEN}[Auto Update] Final Results:{ColorPrint.RESET}")
        print(f"{ColorPrint.GREEN}  ✓ Successful: {len(successful)}{ColorPrint.RESET}")
        print(f"{ColorPrint.RED}  ✗ Failed: {len(final_failed)}{ColorPrint.RESET}")
        
        if final_failed:
            print(f"{ColorPrint.YELLOW}[Auto Update] Failed profiles: {final_failed}{ColorPrint.RESET}")
        
        # Now run the original champion history extraction for successful profiles
        if successful:
            print(f"{ColorPrint.CYAN}[Auto Update] Running champion history extraction for successful profiles{ColorPrint.RESET}")
            EnhancedLeagueChampScraper.update_team_champ_history(tournament_id, team_id, successful, run_update=True)
        
        EnhancedLeagueChampScraper.close()
        
        return results

# Maintain backward compatibility
LeagueChampScraper.auto_update_team_champ_history = EnhancedLeagueChampScraper.auto_update_team_champ_history