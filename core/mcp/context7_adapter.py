import os
import requests
import logging

logger = logging.getLogger(__name__)

class Context7MCPAdapter:
    def __init__(self):
        self.api_key = os.getenv("CONTEXT7_API_KEY")
        self.base_url = os.getenv("CONTEXT7_BASE_URL", "https://api.context7.com")
        self._is_available = bool(self.api_key) # Available if API key is set

    @property
    def is_available(self) -> bool:
        return self._is_available

    def process_query(self, query: str) -> dict:
        if not self.is_available:
            logger.warning("Context7MCPAdapter is not available. API key not set.")
            return {"error": "Context7 API key not configured."}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"query": query}
        url = f"{self.base_url}/process" # Assuming a /process endpoint for queries

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Context7 API: {e}")
            return {"error": f"Context7 API communication error: {e}"}

    def library_resolution(self, package_name: str) -> dict:
        if not self.is_available:
            logger.warning("Context7MCPAdapter is not available. API key not set.")
            return {"error": "Context7 API key not configured."}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"package_name": package_name}
        url = f"{self.base_url}/library_resolution" # Assuming a /library_resolution endpoint

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Context7 API for library resolution: {e}")
            return {"error": f"Context7 API communication error: {e}"}
