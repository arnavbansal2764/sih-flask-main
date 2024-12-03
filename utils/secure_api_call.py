import requests
import random
import time
def exponential_backoff_request(api_call_func, max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        try:
            return api_call_func()  # Attempt the API call
        except requests.RequestException as e:
            wait = min(2 ** attempt + random.uniform(0, 1), 30)  
            print(f"Attempt {attempt + 1} failed; retrying in {wait:.2f} seconds...")
            time.sleep(wait)
            attempt += 1
    raise Exception("Max retry attempts reached")