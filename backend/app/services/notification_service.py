"""Notification service for sending Telegram and email notifications."""

import os
import logging
from datetime import datetime
from typing import Optional
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from sqlalchemy.orm import Session
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

from app.db.models import NotificationPreferences, DeliveryLog, User, Post

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling notifications via Telegram and Email."""
    
    def __init__(self):
        """Initialize the notification service with API credentials."""
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.sender_email = os.getenv("SENDER_EMAIL", "noreply@linkedinghostwriter.com")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        # Initialize Telegram bot if token is available
        self.telegram_bot = None
        if self.telegram_bot_token:
            try:
                self.telegram_bot = Bot(token=self.telegram_bot_token)
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
    
    async def send_telegram_message(
        self,
        chat_id: str,
        message: str,
        post_id: Optional[int] = None,
        include_actions: bool = True
    ) -> tuple[bool, Optional[str]]:
        """
        Send a message via Telegram with optional inline action buttons.
        
        Args:
            chat_id: Telegram chat ID
            message: Message text to send
            post_id: Optional post ID for action buttons
            include_actions: Whether to include action buttons
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.telegram_bot:
            return False, "Telegram bot not configured"
        
        try:
            # Create inline keyboard with action buttons if requested
            reply_markup = None
            if include_actions and post_id:
                keyboard = [
                    [
                        InlineKeyboardButton("👍 Approve", callback_data=f"approve_{post_id}"),
                        InlineKeyboardButton("♻️ Regenerate", callback_data=f"regenerate_{post_id}"),
                        InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{post_id}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            await self.telegram_bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            
            logger.info(f"Telegram message sent successfully to chat_id: {chat_id}")
            return True, None
            
        except TelegramError as e:
            error_msg = f"Telegram error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error sending Telegram message: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send an email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML version of email body
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        if not self.smtp_username or not self.smtp_password:
            return False, "SMTP credentials not configured"
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to: {to_email}")
            return True, None
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    async def send_post_notification(
        self,
        db: Session,
        user_id: int,
        post: Post,
        channel: str
    ) -> tuple[bool, Optional[str]]:
        """
        Send a post notification to the user via the specified channel.
        
        Args:
            db: Database session
            user_id: User ID
            post: Post object to send
            channel: 'email' or 'telegram'
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Get user and preferences
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"
        
        preferences = db.query(NotificationPreferences).filter(
            NotificationPreferences.user_id == user_id
        ).first()
        
        # Check if notification is enabled for this channel
        if preferences:
            if channel == 'email' and not preferences.receive_email_notifications:
                return False, "Email notifications disabled"
            elif channel == 'telegram' and not preferences.receive_telegram_notifications:
                return False, "Telegram notifications disabled"
        
        # Format the message
        message = self._format_post_message(post)
        
        # Send via appropriate channel
        success = False
        error_message = None
        
        if channel == 'telegram':
            if not user.telegram_chat_id:
                error_message = "Telegram chat ID not configured"
            else:
                success, error_message = await self.send_telegram_message(
                    chat_id=user.telegram_chat_id,
                    message=message,
                    post_id=post.id,
                    include_actions=True
                )
        elif channel == 'email':
            subject = "Your LinkedIn Ghostwriter Post Draft"
            html_body = self._format_post_html_email(post)
            success, error_message = self.send_email(
                to_email=user.email,
                subject=subject,
                body=message,
                html_body=html_body
            )
        else:
            error_message = f"Invalid channel: {channel}"
        
        # Log the delivery attempt
        await self.log_delivery(
            db=db,
            user_id=user_id,
            post_id=post.id,
            channel=channel,
            status='delivered' if success else 'failed',
            error_message=error_message
        )
        
        return success, error_message
    
    async def send_daily_reminder(
        self,
        db: Session,
        user_id: int
    ) -> tuple[bool, Optional[str]]:
        """
        Send a daily reminder to post content.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found"
        
        preferences = db.query(NotificationPreferences).filter(
            NotificationPreferences.user_id == user_id
        ).first()
        
        if not preferences or not preferences.daily_reminder_enabled:
            return False, "Daily reminders not enabled"
        
        message = (
            "📅 <b>Daily Reminder</b>\n\n"
            "Time to create your next LinkedIn post! 🚀\n\n"
            "Keep your posting streak going and engage your audience.\n\n"
            "Click here to get started → /create"
        )
        
        # Try Telegram first, fallback to email
        if preferences.receive_telegram_notifications and user.telegram_chat_id:
            success, error = await self.send_telegram_message(
                chat_id=user.telegram_chat_id,
                message=message,
                include_actions=False
            )
            if success:
                await self.log_delivery(db, user_id, None, 'telegram', 'delivered', None)
                return True, None
        
        if preferences.receive_email_notifications:
            success, error = self.send_email(
                to_email=user.email,
                subject="Daily Reminder: Create Your LinkedIn Post",
                body=message.replace('<b>', '').replace('</b>', ''),
                html_body=f"<html><body><p>{message}</p></body></html>"
            )
            if success:
                await self.log_delivery(db, user_id, None, 'email', 'delivered', None)
                return True, None
            return False, error
        
        return False, "No notification channels enabled"
    
    async def log_delivery(
        self,
        db: Session,
        user_id: int,
        post_id: Optional[int],
        channel: str,
        status: str,
        error_message: Optional[str]
    ) -> None:
        """
        Log a notification delivery attempt.
        
        Args:
            db: Database session
            user_id: User ID
            post_id: Optional post ID
            channel: 'email' or 'telegram'
            status: 'delivered', 'failed', or 'retried'
            error_message: Optional error message
        """
        log = DeliveryLog(
            user_id=user_id,
            post_id=post_id,
            channel=channel,
            status=status,
            error_message=error_message
        )
        db.add(log)
        db.commit()
        logger.info(f"Delivery log created: user={user_id}, channel={channel}, status={status}")
    
    def _format_post_message(self, post: Post) -> str:
        """Format a post for notification message."""
        header = "📝 <b>New LinkedIn Post Generated!</b>\n\n"
        content = f"{post.content}\n\n"
        footer = "---\n"
        
        if post.generation_mode == 'auto' and post.template_id:
            footer += f"Generated using template-driven mode\n"
        else:
            footer += f"Generated using manual mode\n"
        
        footer += f"Status: {post.status.title()}"
        
        return header + content + footer
    
    def _format_post_html_email(self, post: Post) -> str:
        """Format a post as HTML email."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #0077B5;">📝 New LinkedIn Post Generated!</h2>
            <div style="background-color: #f3f6f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p style="white-space: pre-wrap; line-height: 1.6;">{post.content}</p>
            </div>
            <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
            <p style="color: #666; font-size: 14px;">
                <strong>Mode:</strong> {post.generation_mode.title()}<br>
                <strong>Status:</strong> {post.status.title()}<br>
                <strong>Created:</strong> {post.created_at.strftime('%Y-%m-%d %H:%M')}
            </p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                This is an automated message from LinkedIn Ghostwriter.
            </p>
        </body>
        </html>
        """
    
    async def retry_send(
        self,
        db: Session,
        user_id: int,
        post_id: int,
        channel: str,
        max_retries: int = 3
    ) -> tuple[bool, Optional[str]]:
        """
        Retry sending a failed notification with exponential backoff.
        
        Args:
            db: Database session
            user_id: User ID
            post_id: Post ID
            channel: 'email' or 'telegram'
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            return False, "Post not found"
        
        for attempt in range(max_retries):
            if attempt > 0:
                # Exponential backoff: 2^attempt seconds
                await asyncio.sleep(2 ** attempt)
                logger.info(f"Retry attempt {attempt + 1}/{max_retries} for post {post_id}")
            
            success, error = await self.send_post_notification(
                db=db,
                user_id=user_id,
                post=post,
                channel=channel
            )
            
            if success:
                # Update the last log to 'retried' status
                if attempt > 0:
                    await self.log_delivery(db, user_id, post_id, channel, 'retried', None)
                return True, None
        
        return False, f"Failed after {max_retries} attempts: {error}"


# Global instance
notification_service = NotificationService()
