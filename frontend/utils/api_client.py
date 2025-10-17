"""API client for communicating with the backend."""

import httpx
from typing import Optional, Dict, Any


class APIClient:
    """Client for interacting with the FastAPI backend."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client."""
        self.base_url = base_url
        self.api_v1 = f"{base_url}/api/v1"
    
    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_v1}/auth/token",
                data={"username": email, "password": password}
            )
            response.raise_for_status()
            return response.json()
    
    async def register(self, email: str, password: str) -> Dict[str, Any]:
        """Register a new user."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_v1}/auth/register",
                json={"email": email, "password": password}
            )
            response.raise_for_status()
            return response.json()
    
    async def generate_post(
        self,
        token: str,
        mode: str,
        message: str,
        template_id: Optional[int] = None,
        post_type: Optional[str] = None,
        tone: Optional[str] = None,
        references: Optional[str] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a new post."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_v1}/posts/",
                headers=self._get_headers(token),
                json={
                    "mode": mode,
                    "message": message,
                    "template_id": template_id,
                    "post_type": post_type,
                    "tone": tone,
                    "references": references,
                    "additional_context": additional_context
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_posts(
        self,
        token: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Dict[str, Any]]:
        """Get user's post history."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/posts/",
                headers=self._get_headers(token),
                params={"skip": skip, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
    
    async def send_post(
        self,
        token: str,
        post_id: int,
        channel: str
    ) -> Dict[str, Any]:
        """Send a post via notification channel."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_v1}/posts/{post_id}/send",
                headers=self._get_headers(token),
                json={"channel": channel}
            )
            response.raise_for_status()
            return response.json()
    
    async def get_templates(self, token: str) -> list[Dict[str, Any]]:
        """Get all available templates."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/templates/",
                headers=self._get_headers(token)
            )
            response.raise_for_status()
            return response.json()
