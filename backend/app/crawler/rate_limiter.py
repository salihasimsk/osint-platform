import time

class RateLimiter:
    def __init__(self,delay_seconds = 2):
        self.delay_seconds = delay_seconds
        self.last_request_time = 0
        
    def wait(self):
        elapsed = time.time() - self.last_request_time
        
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        
        self.last_request_time= time.time()