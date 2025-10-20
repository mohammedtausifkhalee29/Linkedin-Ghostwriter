"""Scheduler service for daily reminders using APScheduler."""

import logging
from datetime import datetime, time as time_obj
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import NotificationPreferences, User
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled tasks like daily reminders."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler."""
        if not self.is_running:
            # Schedule daily reminder check
            # Run every hour to check for users who need reminders
            self.scheduler.add_job(
                self.check_and_send_reminders,
                trigger=CronTrigger(minute=0),  # Run at the start of every hour
                id='daily_reminders_check',
                name='Check and send daily reminders',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler service started successfully")
    
    def stop(self):
        """Stop the scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler service stopped")
    
    async def check_and_send_reminders(self):
        """
        Check for users who have daily reminders enabled and send them.
        
        This function runs every hour and checks if any users have
        their reminder time matching the current hour.
        """
        db: Session = SessionLocal()
        try:
            current_hour = datetime.now().hour
            current_minute = datetime.now().minute
            
            # Get all users with daily reminders enabled
            preferences_list = db.query(NotificationPreferences).filter(
                NotificationPreferences.daily_reminder_enabled == True
            ).all()
            
            logger.info(f"Checking reminders for {len(preferences_list)} users at {current_hour}:{current_minute:02d}")
            
            for prefs in preferences_list:
                # Check if reminder time matches current time (within the hour)
                reminder_time = prefs.daily_reminder_time
                if isinstance(reminder_time, time_obj):
                    reminder_hour = reminder_time.hour
                    reminder_minute = reminder_time.minute
                else:
                    # Handle string format if needed
                    reminder_hour = int(str(reminder_time).split(':')[0])
                    reminder_minute = int(str(reminder_time).split(':')[1])
                
                # Send reminder if time matches (with 15-minute window)
                if reminder_hour == current_hour and abs(reminder_minute - current_minute) < 15:
                    logger.info(f"Sending daily reminder to user {prefs.user_id}")
                    try:
                        await notification_service.send_daily_reminder(
                            db=db,
                            user_id=prefs.user_id
                        )
                    except Exception as e:
                        logger.error(f"Failed to send reminder to user {prefs.user_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error in check_and_send_reminders: {e}")
        finally:
            db.close()
    
    async def send_reminder_now(self, db: Session, user_id: int) -> tuple[bool, Optional[str]]:
        """
        Manually trigger a reminder for a specific user.
        
        Args:
            db: Database session
            user_id: User ID to send reminder to
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        try:
            return await notification_service.send_daily_reminder(db=db, user_id=user_id)
        except Exception as e:
            error_msg = f"Failed to send reminder: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def schedule_custom_reminder(
        self,
        user_id: int,
        reminder_time: time_obj,
        job_id: Optional[str] = None
    ):
        """
        Schedule a custom reminder for a user at a specific time.
        
        Args:
            user_id: User ID
            reminder_time: Time to send the reminder
            job_id: Optional custom job ID
        """
        if job_id is None:
            job_id = f"reminder_user_{user_id}"
        
        # Remove existing job if it exists
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass
        
        # Add new job
        self.scheduler.add_job(
            self.send_user_reminder,
            trigger=CronTrigger(
                hour=reminder_time.hour,
                minute=reminder_time.minute
            ),
            args=[user_id],
            id=job_id,
            name=f"Daily reminder for user {user_id}",
            replace_existing=True
        )
        
        logger.info(f"Scheduled daily reminder for user {user_id} at {reminder_time}")
    
    async def send_user_reminder(self, user_id: int):
        """
        Send a reminder to a specific user.
        
        Args:
            user_id: User ID
        """
        db: Session = SessionLocal()
        try:
            await notification_service.send_daily_reminder(db=db, user_id=user_id)
        except Exception as e:
            logger.error(f"Failed to send reminder to user {user_id}: {e}")
        finally:
            db.close()
    
    def remove_user_reminder(self, user_id: int):
        """
        Remove a scheduled reminder for a user.
        
        Args:
            user_id: User ID
        """
        job_id = f"reminder_user_{user_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed daily reminder for user {user_id}")
        except:
            logger.warning(f"No reminder job found for user {user_id}")


# Global instance
scheduler_service = SchedulerService()
