 import requests
import pandas as pd
import time
from cache_manager import CacheManager

class DataFetcher:
    def __init__(self):
        self.cache = CacheManager()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Kenya-SDG-Dashboard/1.0'})
    
    def get_knbs_data(self, endpoint, params=None):
        """Fetch from KNBS API"""
        cache_key = f"knbs_{endpoint}_{str(params)}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # In production, use actual KNBS API
            # response = self.session.get(f"https://www.knbs.or.ke/api/{endpoint}", params=params)
            # data = response.json()
            
            # For demo, return structured mock data
            data = self._mock_knbs_data(endpoint)
            self.cache.set(cache_key, data)
            return data
        except Exception as e:
            print(f"KNBS API error: {e}")
            return None
    
    def _mock_knbs_data(self, endpoint):
        """Mock KNBS data for demonstration"""
        mocks = {
            "population": {"total": 47500000, "urban": 0.28, "rural": 0.72},
            "gdp": {"value": 95.5, "growth": 5.2, "year": 2025},
            "cpi": {"value": 5.8, "trend": [5.7, 5.9, 6.1, 5.8]},
            "poverty": {"rate": 36.1, "rural_poverty": 40.1, "urban_poverty": 29.4}
        }
        return mocks.get(endpoint, {})