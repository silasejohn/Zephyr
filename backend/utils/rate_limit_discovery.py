##########################
### Rate Limit Discovery ##
##########################

"""
[info] Utility for discovering optimal rate limits for rewind.lol

This module provides tools to safely discover the exact rate limits
for rewind.lol by gradually increasing request frequency until limits are hit.
"""

import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict

# Local imports
from modules.scrapers.enhanced_rewind_scraper import EnhancedLeagueChampScraper, ProfileManager
import modules.utils.color_utils as ColorPrint

@dataclass
class RateLimitTest:
    """Data class for tracking rate limit test results"""
    test_time: datetime
    profiles_tested: List[str]
    time_interval_seconds: int
    success_count: int
    captcha_triggered: bool
    queue_overflow: bool
    notes: str = ""

class RateLimitDiscovery:
    """
    [info] Discovers optimal rate limits through controlled testing
    
    Uses binary search approach to find the exact time-window limits
    that trigger reCAPTCHA or queue overflow errors.
    """
    
    def __init__(self, test_profiles: List[str]):
        """
        [param] test_profiles: List[str] - Safe profiles to test with
        """
        self.test_profiles = test_profiles
        self.test_results: List[RateLimitTest] = []
        self.discovered_limits = {
            "concurrent_limit": 5,  # Known from documentation
            "time_window_seconds": None,  # To be discovered
            "safe_interval_seconds": None,  # To be discovered
            "captcha_cooldown_minutes": None  # To be discovered
        }
        
    def run_discovery_test(self, interval_seconds: int, max_profiles: int = 3) -> RateLimitTest:
        """
        [info] Runs a single rate limit discovery test
        
        [param] interval_seconds: int - Time interval between requests
        [param] max_profiles: int - Maximum profiles to test
        [return] RateLimitTest: Results of the test
        """
        print(f"{ColorPrint.CYAN}[Rate Discovery] Testing {interval_seconds}s intervals with {max_profiles} profiles{ColorPrint.RESET}")
        
        # Setup scraper
        EnhancedLeagueChampScraper.set_up_rewind_lol()
        profile_manager = ProfileManager(EnhancedLeagueChampScraper.DRIVER)
        
        test_start = datetime.now()
        profiles_to_test = self.test_profiles[:max_profiles]
        success_count = 0
        captcha_triggered = False
        queue_overflow = False
        
        try:
            for i, profile in enumerate(profiles_to_test):
                print(f"{ColorPrint.YELLOW}[Rate Discovery] Testing profile {i+1}/{len(profiles_to_test)}: {profile}{ColorPrint.RESET}")
                
                # Attempt to search profile
                status = profile_manager.search_profile(profile)
                
                if "recaptcha" in EnhancedLeagueChampScraper.DRIVER.page_source.lower():
                    captcha_triggered = True
                    print(f"{ColorPrint.RED}[Rate Discovery] CAPTCHA triggered at profile {i+1}{ColorPrint.RESET}")
                    break
                
                if "too many requests" in EnhancedLeagueChampScraper.DRIVER.page_source.lower():
                    queue_overflow = True
                    print(f"{ColorPrint.RED}[Rate Discovery] Queue overflow at profile {i+1}{ColorPrint.RESET}")
                    break
                
                success_count += 1
                
                # Wait specified interval before next request (except for last)
                if i < len(profiles_to_test) - 1:
                    print(f"{ColorPrint.CYAN}[Rate Discovery] Waiting {interval_seconds}s...{ColorPrint.RESET}")
                    time.sleep(interval_seconds)
        
        except Exception as e:
            print(f"{ColorPrint.RED}[Rate Discovery] Error during test: {e}{ColorPrint.RESET}")
        
        finally:
            EnhancedLeagueChampScraper.close()
        
        # Create test result
        test_result = RateLimitTest(
            test_time=test_start,
            profiles_tested=profiles_to_test,
            time_interval_seconds=interval_seconds,
            success_count=success_count,
            captcha_triggered=captcha_triggered,
            queue_overflow=queue_overflow,
            notes=f"Tested {len(profiles_to_test)} profiles with {interval_seconds}s intervals"
        )
        
        self.test_results.append(test_result)
        return test_result
    
    def binary_search_optimal_interval(self, min_interval: int = 5, max_interval: int = 120) -> int:
        """
        [info] Uses binary search to find optimal request interval
        
        [param] min_interval: int - Minimum interval to test (seconds)
        [param] max_interval: int - Maximum interval to test (seconds)
        [return] int: Optimal interval in seconds
        """
        print(f"{ColorPrint.MAGENTA}[Rate Discovery] Starting binary search for optimal interval{ColorPrint.RESET}")
        print(f"{ColorPrint.MAGENTA}[Rate Discovery] Range: {min_interval}s - {max_interval}s{ColorPrint.RESET}")
        
        while min_interval < max_interval:
            mid_interval = (min_interval + max_interval) // 2
            
            print(f"{ColorPrint.CYAN}[Rate Discovery] Testing interval: {mid_interval}s{ColorPrint.RESET}")
            
            # Test with current interval
            result = self.run_discovery_test(mid_interval, max_profiles=3)
            
            if result.captcha_triggered or result.queue_overflow:
                # This interval is too aggressive, increase it
                min_interval = mid_interval + 1
                print(f"{ColorPrint.YELLOW}[Rate Discovery] Interval too aggressive, trying higher{ColorPrint.RESET}")
            else:
                # This interval worked, try a more aggressive one
                max_interval = mid_interval
                print(f"{ColorPrint.GREEN}[Rate Discovery] Interval successful, trying lower{ColorPrint.RESET}")
            
            # Add cooldown between tests
            print(f"{ColorPrint.CYAN}[Rate Discovery] Cooldown period (60s)...{ColorPrint.RESET}")
            time.sleep(60)
        
        optimal_interval = min_interval
        print(f"{ColorPrint.GREEN}[Rate Discovery] Optimal interval discovered: {optimal_interval}s{ColorPrint.RESET}")
        
        self.discovered_limits["time_window_seconds"] = optimal_interval * 3  # Conservative time window
        self.discovered_limits["safe_interval_seconds"] = optimal_interval
        
        return optimal_interval
    
    def test_captcha_cooldown(self) -> int:
        """
        [info] Tests how long to wait after triggering a captcha
        
        [return] int: Recommended cooldown time in minutes
        """
        print(f"{ColorPrint.MAGENTA}[Rate Discovery] Testing captcha cooldown period{ColorPrint.RESET}")
        
        # Deliberately trigger a captcha with aggressive testing
        result = self.run_discovery_test(interval_seconds=1, max_profiles=6)
        
        if not result.captcha_triggered:
            print(f"{ColorPrint.YELLOW}[Rate Discovery] Could not trigger captcha for cooldown test{ColorPrint.RESET}")
            return 10  # Default 10 minutes
        
        captcha_time = datetime.now()
        
        # Test recovery at different intervals
        for cooldown_minutes in [5, 10, 15, 20]:
            print(f"{ColorPrint.CYAN}[Rate Discovery] Waiting {cooldown_minutes} minutes after captcha...{ColorPrint.RESET}")
            time.sleep(cooldown_minutes * 60)
            
            # Test if we can make requests again
            recovery_result = self.run_discovery_test(interval_seconds=30, max_profiles=1)
            
            if not recovery_result.captcha_triggered:
                print(f"{ColorPrint.GREEN}[Rate Discovery] Recovered after {cooldown_minutes} minutes{ColorPrint.RESET}")
                self.discovered_limits["captcha_cooldown_minutes"] = cooldown_minutes
                return cooldown_minutes
        
        print(f"{ColorPrint.RED}[Rate Discovery] Could not determine captcha cooldown{ColorPrint.RESET}")
        return 20  # Conservative default
    
    def run_full_discovery(self) -> Dict:
        """
        [info] Runs complete rate limit discovery process
        
        [return] Dict: Discovered rate limits
        """
        print(f"{ColorPrint.MAGENTA}[Rate Discovery] Starting full rate limit discovery{ColorPrint.RESET}")
        print(f"{ColorPrint.MAGENTA}[Rate Discovery] Test profiles: {self.test_profiles}{ColorPrint.RESET}")
        
        # Step 1: Find optimal interval
        optimal_interval = self.binary_search_optimal_interval()
        
        # Step 2: Test captcha cooldown
        cooldown_time = self.test_captcha_cooldown()
        
        # Step 3: Validate findings with conservative test
        print(f"{ColorPrint.CYAN}[Rate Discovery] Validating findings with conservative test{ColorPrint.RESET}")
        validation_result = self.run_discovery_test(interval_seconds=optimal_interval + 10, max_profiles=2)
        
        if validation_result.captcha_triggered or validation_result.queue_overflow:
            print(f"{ColorPrint.YELLOW}[Rate Discovery] Validation failed, adjusting limits{ColorPrint.RESET}")
            self.discovered_limits["safe_interval_seconds"] = optimal_interval + 20
            self.discovered_limits["time_window_seconds"] = (optimal_interval + 20) * 3
        
        print(f"{ColorPrint.GREEN}[Rate Discovery] Discovery complete!{ColorPrint.RESET}")
        self._print_results()
        
        return self.discovered_limits
    
    def save_results(self, filename: str = "rate_limit_discovery_results.json"):
        """
        [info] Saves discovery results to JSON file
        
        [param] filename: str - Output filename
        """
        results_data = {
            "discovery_date": datetime.now().isoformat(),
            "test_profiles": self.test_profiles,
            "discovered_limits": self.discovered_limits,
            "test_results": [asdict(result) for result in self.test_results]
        }
        
        # Convert datetime objects to strings for JSON serialization
        for test in results_data["test_results"]:
            test["test_time"] = test["test_time"].isoformat()
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"{ColorPrint.GREEN}[Rate Discovery] Results saved to {filename}{ColorPrint.RESET}")
    
    def _print_results(self):
        """
        [info] Prints formatted results summary
        """
        print(f"\n{ColorPrint.MAGENTA}==== RATE LIMIT DISCOVERY RESULTS ===={ColorPrint.RESET}")
        print(f"{ColorPrint.CYAN}Concurrent Limit: {self.discovered_limits['concurrent_limit']}{ColorPrint.RESET}")
        print(f"{ColorPrint.CYAN}Safe Interval: {self.discovered_limits['safe_interval_seconds']}s{ColorPrint.RESET}")
        print(f"{ColorPrint.CYAN}Time Window: {self.discovered_limits['time_window_seconds']}s{ColorPrint.RESET}")
        print(f"{ColorPrint.CYAN}Captcha Cooldown: {self.discovered_limits['captcha_cooldown_minutes']} minutes{ColorPrint.RESET}")
        
        print(f"\n{ColorPrint.YELLOW}Test Summary:{ColorPrint.RESET}")
        for i, result in enumerate(self.test_results):
            status = "FAILED" if (result.captcha_triggered or result.queue_overflow) else "SUCCESS"
            color = ColorPrint.RED if status == "FAILED" else ColorPrint.GREEN
            print(f"  Test {i+1}: {color}{status}{ColorPrint.RESET} - {result.time_interval_seconds}s interval, {result.success_count} successful")

def main():
    """
    [info] Main function for running rate limit discovery
    """
    # Example test profiles - replace with actual profiles you can safely test
    test_profiles = [
        "TestUser1#NA1",
        "TestUser2#NA1", 
        "TestUser3#NA1",
        "TestUser4#NA1",
        "TestUser5#NA1"
    ]
    
    print(f"{ColorPrint.MAGENTA}WARNING: Rate limit discovery will make multiple requests to rewind.lol{ColorPrint.RESET}")
    print(f"{ColorPrint.MAGENTA}Make sure you have permission and the test profiles are safe to use.{ColorPrint.RESET}")
    
    response = input("Continue with discovery? (y/N): ")
    if response.lower() != 'y':
        print("Discovery cancelled.")
        return
    
    # Run discovery
    discovery = RateLimitDiscovery(test_profiles)
    limits = discovery.run_full_discovery()
    discovery.save_results()
    
    return limits

if __name__ == "__main__":
    main()