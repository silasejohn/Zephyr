# data_models/api_queue.py
from queue import Queue
import time
import logging
from threading import Thread

logging.basicConfig(level=logging.INFO)

class APIQueue:
    """
    [info] Queue manager for API requests with rate limiting and retry logic
    """
    def __init__(self, rate_limit: int, interval: float) -> None:
        """
        [info] Initialize API queue with rate limiting parameters
        [param] rate_limit: Maximum number of requests per interval
        [param] interval: Time interval in seconds between requests
        [return] None
        """
        self.queue = Queue()
        self.rate_limit = rate_limit
        self.interval = interval
        self.last_request_time = time.time()

        # Create a thread to process the queue (background, runs process_queue())
        self.processing_thread = Thread(target=self.process_queue)
        self.processing_thread.daemon = True    # don't prevent program from exiting
        self.processing_thread.start()          # start the thread

    def add_to_queue(self, api_object) -> None:
        """
        [info] Add an API object to the processing queue
        [param] api_object: APIObject instance to be queued
        [return] None
        """
        self.queue.put(api_object)
        logging.info(f"Added to queue: {api_object.url}")

    def process_queue(self) -> None:
        """
        [info] Background thread function to process queued API requests with rate limiting
        [return] None
        """
        while True:
            if not self.queue.empty():
                current_time = time.time()
                if current_time - self.last_request_time >= self.interval:
                    api_object = self.queue.get()
                    response = api_object.make_request()
                    self.last_request_time = current_time
                    
                    if response and response.status_code < 500:
                        api_object.callback(response)
                    else:
                        if api_object.retry_attempts > 0:
                            api_object.retry_attempts -= 1
                            self.queue.put(api_object)
                            logging.warning(f"Retrying: {api_object.url}")
                        else:
                            logging.error(f"Max retries reached for: {api_object.url}")
            else:
                time.sleep(1)
