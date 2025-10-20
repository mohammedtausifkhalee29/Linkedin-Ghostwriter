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
    
    async def get_notification_settings(self, token: str) -> Dict[str, Any]:
        """Get user's notification settings."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/notifications/settings",
                headers=self._get_headers(token)
            )
            response.raise_for_status()
            return response.json()
    
    async def update_notification_settings(
        self,
        token: str,
        receive_email_notifications: Optional[bool] = None,
        receive_telegram_notifications: Optional[bool] = None,
        daily_reminder_enabled: Optional[bool] = None,
        daily_reminder_time: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user's notification settings."""
        data = {}
        if receive_email_notifications is not None:
            data["receive_email_notifications"] = receive_email_notifications
        if receive_telegram_notifications is not None:
            data["receive_telegram_notifications"] = receive_telegram_notifications
        if daily_reminder_enabled is not None:
            data["daily_reminder_enabled"] = daily_reminder_enabled
        if daily_reminder_time is not None:
            data["daily_reminder_time"] = daily_reminder_time
        if telegram_chat_id is not None:
            data["telegram_chat_id"] = telegram_chat_id
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.api_v1}/notifications/settings",
                headers=self._get_headers(token),
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_delivery_logs(
        self,
        token: str,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get delivery logs with pagination."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/notifications/logs",
                headers=self._get_headers(token),
                params={"page": page, "limit": limit}
            )
            response.raise_for_status()
            return response.json()
    
    async def send_post_notification(
        self,
        token: str,
        post_id: int,
        channel: str
    ) -> Dict[str, Any]:
        """Send a post notification via specified channel."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_v1}/notifications/posts/{post_id}/send",
                headers=self._get_headers(token),
                json={"channel": channel}
            )
            response.raise_for_status()
            return response.json()
    
    # Template Management Methods
    
    async def get_templates_filtered(
        self,
        token: str,
        category: Optional[str] = None,
        tone: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get templates with optional filtering."""
        params = {"skip": skip, "limit": limit}
        if category:
            params["category"] = category
        if tone:
            params["tone"] = tone
        if search:
            params["search"] = search
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/templates/",
                headers=self._get_headers(token),
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_template(self, token: str, template_id: int) -> Dict[str, Any]:
        """Get a specific template by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/templates/{template_id}",
                headers=self._get_headers(token)
            )
            response.raise_for_status()
            return response.json()
    
    async def create_template(
        self,
        token: str,
        name: str,
        category: str,
        prompt: str,
        structure: str,
        tone: str = "Professional",
        example: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new template."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_v1}/templates/",
                headers=self._get_headers(token),
                json={
                    "name": name,
                    "category": category,
                    "prompt": prompt,
                    "structure": structure,
                    "tone": tone,
                    "example": example
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def update_template(
        self,
        token: str,
        template_id: int,
        name: Optional[str] = None,
        category: Optional[str] = None,
        prompt: Optional[str] = None,
        structure: Optional[str] = None,
        tone: Optional[str] = None,
        example: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a template (automatically versions if needed)."""
        data = {}
        if name is not None:
            data["name"] = name
        if category is not None:
            data["category"] = category
        if prompt is not None:
            data["prompt"] = prompt
        if structure is not None:
            data["structure"] = structure
        if tone is not None:
            data["tone"] = tone
        if example is not None:
            data["example"] = example
            
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.api_v1}/templates/{template_id}",
                headers=self._get_headers(token),
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_template(self, token: str, template_id: int) -> None:
        """Delete a template."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.api_v1}/templates/{template_id}",
                headers=self._get_headers(token)
            )
            response.raise_for_status()
    
    async def get_template_versions(
        self,
        token: str,
        template_id: int
    ) -> list[Dict[str, Any]]:
        """Get version history for a template."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/templates/{template_id}/versions",
                headers=self._get_headers(token)
            )
            response.raise_for_status()
            return response.json()
    
    async def get_template_stats(self, token: str) -> Dict[str, Any]:
        """Get template statistics."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_v1}/templates/stats",
                headers=self._get_headers(token)
            )
            response.raise_for_status()
            return response.json()
    
    # Post Management Methods
    
    async def publish_draft(self, token: str, post_id: int) -> Dict[str, Any]:
        """Publish a draft post."""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.api_v1}/posts/{post_id}/publish",
                headers=self._get_headers(token)
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_post(self, token: str, post_id: int) -> None:
        """Delete a post."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.api_v1}/posts/{post_id}",
                headers=self._get_headers(token)
            )
            response.raise_for_status()
