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
        post_type: str,
        message: str,
        tone: str,
        reference_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a new post."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.api_v1}/posts/generate",
                headers=self._get_headers(token),
                json={
                    "post_type": post_type,
                    "message": message,
                    "tone": tone,
                    "reference_text": reference_text
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def save_draft(
        self,
        token: str,
        content: str,
        reference_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save a post as draft."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_v1}/posts/draft",
                headers=self._get_headers(token),
                json={
                    "content": content,
                    "reference_text": reference_text
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def send_post(
        self,
        token: str,
        post_content: str,
        channel: str
    ) -> Dict[str, Any]:
        """Send a post via notification channel."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_v1}/posts/send",
                headers=self._get_headers(token),
                json={
                    "post_content": post_content,
                    "channel": channel
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_posts(
        self,
        token: str,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """Get user's post history."""
        params = {"skip": skip, "limit": limit}
        if status_filter:
            params["status_filter"] = status_filter
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/posts/",
                headers=self._get_headers(token),
                params=params
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
    
    async def generate_auto_post(
        self,
        token: str,
        template_id: int,
        message: str,
        tone: str,
        reference_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a post using a template (Auto Post Mode)."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.api_v1}/posts/generate-auto",
                headers=self._get_headers(token),
                json={
                    "template_id": template_id,
                    "message": message,
                    "tone": tone,
                    "reference_text": reference_text
                }
            )
            response.raise_for_status()
            return response.json()
