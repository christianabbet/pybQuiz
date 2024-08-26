import time
import requests
from typing import Optional
import numpy as np


STATUS_OK = 200

HEADERS_SCRAP = {
    # Means we arrive from google service
    'Referer': 'https://www.google.com/',
    # Means we are a linux like system
    # 'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/26.0 Chrome/122.0.0.0 Mobile Safari/537.3',
}



def check_code(status_code: int):
    return status_code == STATUS_OK


def slow_request(url: str, params: Optional[dict] = None, delay: Optional[float] = 3.0):

    # Add random delays to avoid detections
    delay = delay * (0.5 + np.random.rand())
        
    # Build request
    start = time.time()    
    page = requests.get(
        url, 
        headers=HEADERS_SCRAP,
        params=params
    )
    is_valid = check_code(status_code=page.status_code)
    end = time.time()

    # Wait for api time
    time.sleep(max(delay - (end - start), 0)) 
    
    # If not valid
    if not is_valid:
        return None
                
    return page
        