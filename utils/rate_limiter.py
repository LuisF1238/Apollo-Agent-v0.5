"""Rate limiting utilities for API calls"""
import time
from collections import deque
from typing import Optional
from datetime import datetime, timedelta


class RateLimiter:
    """
    Token bucket rate limiter for API calls
    
    Attributes:
        max_requests: Maximum number of requests allowed per time window
        time_window: Time window in seconds
    """
    
    def __init__(self, max_requests: int, time_window: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds (default: 60)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def can_make_request(self) -> bool:
        """
        Check if a request can be made without exceeding the rate limit
        
        Returns:
            True if request can be made, False otherwise
        """
        now = time.time()
        
        # Remove requests outside the time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        return len(self.requests) < self.max_requests
    
    def wait_time(self) -> float:
        """
        Calculate how long to wait before making the next request
        
        Returns:
            Wait time in seconds (0 if can make request now)
        """
        if self.can_make_request():
            return 0.0
        
        # Time until oldest request exits the window
        now = time.time()
        oldest_request = self.requests[0]
        wait = oldest_request + self.time_window - now
        
        return max(0.0, wait)
    
    def acquire(self, block: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request
        
        Args:
            block: Whether to block until permission is granted
            timeout: Maximum time to wait in seconds (None = wait forever)
            
        Returns:
            True if permission granted, False if timeout or non-blocking and rate limited
        """
        start_time = time.time()
        
        while True:
            if self.can_make_request():
                self.requests.append(time.time())
                return True
            
            if not block:
                return False
            
            wait = self.wait_time()
            
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return False
                wait = min(wait, timeout - elapsed)
            
            if wait > 0:
                time.sleep(wait)
    
    def reset(self):
        """Reset the rate limiter"""
        self.requests.clear()
    
    def __repr__(self) -> str:
        return f"RateLimiter(max_requests={self.max_requests}, time_window={self.time_window})"


__all__ = ["RateLimiter"]
