import requests
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class WebhookService:
    def __init__(self, base_url: str, default_headers: Optional[Dict[str, str]] = None, timeout: int = 5):
        self.base_url = base_url
        self.default_headers = default_headers or {}
        self.timeout = timeout

    def post(self, endpoint: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        final_headers = {**self.default_headers, **(headers or {})}

        try:
            response = requests.post(url, json=payload, headers=final_headers, timeout=self.timeout)
            response.raise_for_status()
            logger.info(f"Webhook POST to {url} succeeded with status {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"Failed to POST webhook to {url}: {e}")
            raise
