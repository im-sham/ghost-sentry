"""Satellite data client for Sentinel-2."""
import os
import httpx
import logging
from typing import List, Optional
from ghost_sentry.core.detector import Detection
from dotenv import load_dotenv

load_dotenv()

class SentinelClient:
    """Client for interacting with Sentinel Hub / Sentinel-2 data."""
    
    def __init__(self):
        self.client_id = os.getenv("SENTINEL_CLIENT_ID")
        self.client_secret = os.getenv("SENTINEL_CLIENT_SECRET")
        self.base_url = "https://services.sentinel-hub.com"
        self.token = None

    async def authenticate(self) -> bool:
        """Authenticate with Sentinel Hub."""
        if not self.client_id or not self.client_secret:
            logging.warning("Sentinel credentials missing. Operating in MOCK mode.")
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(
                    f"{self.base_url}/auth/realms/main/protocol/openid-connect/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                res.raise_for_status()
                self.token = res.json().get("access_token")
                return True
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            return False

    async def get_latest_image_path(self, bbox: List[float]) -> Optional[str]:
        """
        Query for the latest Sentinel-2 image for a bounding box.
        Returns the local path to the downloaded image or None.
        
        Currently, this is a placeholder structural implementation.
        """
        if not self.token:
            return None
            
        # Structural implementation for future API calls
        logging.info(f"Querying Sentinel-2 for bbox: {bbox}")
        return "path/to/downloaded/sentinel_image.jpg"

def get_satellite_client():
    """Factory for getting the client."""
    return SentinelClient()
