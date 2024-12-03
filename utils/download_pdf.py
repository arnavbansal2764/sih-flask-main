import requests
import os
from utils.secure_api_call import exponential_backoff_request
def download_pdf(url, save_path):
    def api_call():
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()  # Raises an HTTPError for unsuccessful requests
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(1024):  # Download in chunks
                f.write(chunk)
        return {"success": True}

    try:
        return exponential_backoff_request(api_call)
    except Exception as e:
        return {"error": f"Failed to download PDF: {str(e)}"}