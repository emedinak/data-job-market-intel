import requests
from .config import ADZUNA_APP_ID, ADZUNA_APP_KEY, COUNTRY

BASE_URL = "https://api.adzuna.com/v1/api/jobs"

class AdzunaClient:
    def search_jobs(self, keyword: str, page: int = 1, results_per_page: int = 20):
        url = f"{BASE_URL}/{COUNTRY}/search/{page}"
        
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": results_per_page,
            "what": keyword,
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
