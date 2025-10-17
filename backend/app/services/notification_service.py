"""Notification service for Telegram and Email."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

import httpx

from app.core.config import settings


class NotificationService:
    """Service for sending notifications via Telegram and Email."""
    
    async def send_telegram(self, chat_id: str, message: str) -> bool:
        """
        Send a message via Telegram Bot API.
        
        Args:
            chat_id: Telegram chat ID
            message: Message content to send
            
        Returns:
            True if successful, False otherwise
        """
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("Telegram bot token not configured")
        
        # TODO: Implement actual Telegram sending logic
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={"chat_id": chat_id, "text": message}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str
    ) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            recipient: Email recipient
            subject: Email subject
            body: Email body content
            
        Returns:
            True if successful, False otherwise
        """
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
            raise ValueError("SMTP settings not configured")
        
        # TODO: Implement actual email sending logic
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM_EMAIL
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            # server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            # server.starttls()
            # server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            # server.send_message(msg)
            # server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
