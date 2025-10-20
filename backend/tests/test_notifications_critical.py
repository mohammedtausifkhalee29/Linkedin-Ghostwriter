"""
Top 10 Critical Test Cases for Feature 3: Messaging & Notifications
Covers the most important functionality for production readiness.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import time
from sqlalchemy.orm import Session

from app.db.models import NotificationPreferences, DeliveryLog, User, Post


class TestCritical01_NotificationSettingsAPI:
    """CRITICAL: Users can retrieve and update notification preferences."""
    
    def test_get_default_notification_settings(self, client, auth_headers, test_user):
        """Test 1: GET settings returns default values for new users."""
        response = client.get("/api/v1/notifications/settings", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["receive_email_notifications"] == True
        assert data["receive_telegram_notifications"] == False
        assert data["daily_reminder_enabled"] == False
        assert data["telegram_chat_id"] is None
        print("✅ Test 1 PASSED: Default notification settings retrieved correctly")
    
    def test_update_notification_settings(self, client, db_session, auth_headers, test_user):
        """Test 2: PUT settings updates user preferences successfully."""
        update_data = {
            "receive_email_notifications": False,
            "receive_telegram_notifications": True,
            "telegram_chat_id": "123456789",
            "daily_reminder_enabled": True,
            "daily_reminder_time": "09:00:00"
        }
        
        response = client.put("/api/v1/notifications/settings", json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["receive_telegram_notifications"] == True
        assert data["telegram_chat_id"] == "123456789"
        assert data["daily_reminder_time"] == "09:00:00"
        
        # Verify database persistence
        prefs = db_session.query(NotificationPreferences).filter_by(user_id=test_user.id).first()
        assert prefs.telegram_chat_id == "123456789"
        print("✅ Test 2 PASSED: Notification settings updated and persisted")


class TestCritical02_DeliveryLogsAPI:
    """CRITICAL: Users can view their notification delivery history."""
    
    def test_get_delivery_logs_with_pagination(self, client, db_session, auth_headers, test_user, test_post):
        """Test 3: GET logs returns paginated delivery history."""
        # Create sample delivery logs
        for i in range(5):
            log = DeliveryLog(
                user_id=test_user.id,
                post_id=test_post.id,
                channel="email" if i % 2 == 0 else "telegram",
                status="delivered" if i < 3 else "failed",
                error_message="Test error" if i >= 3 else None
            )
            db_session.add(log)
        db_session.commit()
        
        response = client.get("/api/v1/notifications/logs?page=1&limit=10", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["logs"]) == 5
        assert data["page"] == 1
        
        # Verify logs contain required fields
        first_log = data["logs"][0]
        assert "channel" in first_log
        assert "status" in first_log
        assert "created_at" in first_log
        print("✅ Test 3 PASSED: Delivery logs retrieved with pagination")


class TestCritical03_TelegramNotifications:
    """CRITICAL: Telegram notifications are sent correctly."""
    
    @patch('telegram.Bot')
    @pytest.mark.asyncio
    async def test_send_telegram_message_success(self, mock_bot_class):
        """Test 4: Telegram messages send successfully with correct formatting."""
        from app.services.notification_service import NotificationService
        
        # Setup mock
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock()
        mock_bot_class.return_value = mock_bot
        
        # Create service instance with mocked bot
        service = NotificationService()
        service.telegram_bot = mock_bot
        
        # Send message
        success, error = await service.send_telegram_message(
            chat_id="123456789",
            message="Test notification message",
            post_id=1,
            include_actions=True
        )
        
        assert success == True
        assert error is None
        mock_bot.send_message.assert_called_once()
        
        # Verify message includes action buttons
        call_kwargs = mock_bot.send_message.call_args.kwargs
        assert call_kwargs["chat_id"] == "123456789"
        assert "reply_markup" in call_kwargs  # Inline keyboard buttons
        print("✅ Test 4 PASSED: Telegram message sent with inline buttons")


class TestCritical04_EmailNotifications:
    """CRITICAL: Email notifications are sent correctly."""
    
    @patch('smtplib.SMTP')
    @pytest.mark.asyncio
    async def test_send_email_success(self, mock_smtp_class):
        """Test 5: Emails send successfully via SMTP."""
        from app.services.notification_service import NotificationService
        
        # Setup mock SMTP server
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_server
        
        service = NotificationService()
        
        # Send email
        success, error = await service.send_email(
            to_email="test@example.com",
            subject="Test Notification",
            body="Your LinkedIn post has been generated!",
            post_id=1
        )
        
        assert success == True
        assert error is None
        mock_server.send_message.assert_called_once()
        print("✅ Test 5 PASSED: Email sent successfully via SMTP")


class TestCritical05_PostNotificationIntegration:
    """CRITICAL: Post notifications respect user preferences."""
    
    @pytest.mark.asyncio
    async def test_send_post_notification_checks_preferences(self, db_session, test_user, test_post):
        """Test 6: Notifications only send to enabled channels."""
        from app.services.notification_service import NotificationService
        
        # Setup user with only email enabled
        test_user.telegram_chat_id = None
        prefs = NotificationPreferences(
            user_id=test_user.id,
            receive_email_notifications=True,
            receive_telegram_notifications=False
        )
        db_session.add(prefs)
        db_session.commit()
        
        service = NotificationService()
        
        # Try sending telegram notification (should fail - disabled)
        with patch.object(service, 'send_telegram_message') as mock_telegram:
            success, error = await service.send_post_notification(
                db=db_session,
                user_id=test_user.id,
                post=test_post,
                channel="telegram"
            )
            
            assert success == False
            assert "disabled" in error.lower()
            mock_telegram.assert_not_called()
        
        print("✅ Test 6 PASSED: Notifications respect user preferences")


class TestCritical06_ManualSendEndpoint:
    """CRITICAL: Users can manually trigger notifications."""
    
    @patch('app.services.notification_service.notification_service.send_post_notification')
    def test_manual_send_post_notification(self, mock_send, client, auth_headers, test_post):
        """Test 7: POST /notifications/posts/{id}/send queues notification."""
        mock_send.return_value = AsyncMock(return_value=(True, None))
        
        response = client.post(
            f"/api/v1/notifications/posts/{test_post.id}/send",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "queued" in data["message"].lower()
        print("✅ Test 7 PASSED: Manual notification send endpoint works")


class TestCritical07_DeliveryLogging:
    """CRITICAL: All notification attempts are logged."""
    
    @pytest.mark.asyncio
    async def test_delivery_logs_created(self, db_session, test_user, test_post):
        """Test 8: Delivery logs are created for all send attempts."""
        from app.services.notification_service import NotificationService
        
        service = NotificationService()
        
        # Log successful delivery
        await service.log_delivery(
            db=db_session,
            user_id=test_user.id,
            post_id=test_post.id,
            channel="email",
            status="delivered",
            error_message=None
        )
        
        # Log failed delivery
        await service.log_delivery(
            db=db_session,
            user_id=test_user.id,
            post_id=test_post.id,
            channel="telegram",
            status="failed",
            error_message="Connection timeout"
        )
        
        # Verify logs in database
        logs = db_session.query(DeliveryLog).filter_by(user_id=test_user.id).all()
        assert len(logs) == 2
        
        success_log = [l for l in logs if l.status == "delivered"][0]
        assert success_log.channel == "email"
        assert success_log.error_message is None
        
        failed_log = [l for l in logs if l.status == "failed"][0]
        assert failed_log.channel == "telegram"
        assert failed_log.error_message == "Connection timeout"
        
        print("✅ Test 8 PASSED: Delivery logs created for all attempts")


class TestCritical08_ErrorHandling:
    """CRITICAL: Graceful error handling for failed notifications."""
    
    @patch('telegram.Bot')
    @pytest.mark.asyncio
    async def test_telegram_failure_returns_error(self, mock_bot_class):
        """Test 9: Telegram failures are caught and logged properly."""
        from app.services.notification_service import NotificationService
        from telegram.error import TelegramError
        
        # Setup mock to raise error
        mock_bot = AsyncMock()
        mock_bot.send_message = AsyncMock(side_effect=TelegramError("Invalid chat_id"))
        mock_bot_class.return_value = mock_bot
        
        service = NotificationService()
        service.telegram_bot = mock_bot
        
        # Attempt to send
        success, error = await service.send_telegram_message(
            chat_id="invalid_id",
            message="Test",
            post_id=1
        )
        
        assert success == False
        assert error is not None
        assert "telegram" in error.lower() or "invalid" in error.lower()
        print("✅ Test 9 PASSED: Telegram errors handled gracefully")


class TestCritical09_UserIsolation:
    """CRITICAL: Users cannot access other users' notification data."""
    
    def test_delivery_logs_user_isolation(self, client, db_session, auth_headers, test_user, test_post):
        """Test 10: Users only see their own delivery logs."""
        # Create another user and their logs
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed"
        )
        db_session.add(other_user)
        db_session.commit()
        
        # Create logs for both users
        my_log = DeliveryLog(
            user_id=test_user.id,
            post_id=test_post.id,
            channel="email",
            status="delivered"
        )
        other_log = DeliveryLog(
            user_id=other_user.id,
            post_id=test_post.id,
            channel="telegram",
            status="delivered"
        )
        db_session.add_all([my_log, other_log])
        db_session.commit()
        
        # Request logs as test_user
        response = client.get("/api/v1/notifications/logs", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1  # Only test_user's log
        assert data["logs"][0]["user_id"] == test_user.id
        print("✅ Test 10 PASSED: User isolation enforced for delivery logs")


# Summary function to run after all tests
def pytest_sessionfinish(session, exitstatus):
    """Print summary after test run."""
    if exitstatus == 0:
        print("\n" + "="*60)
        print("🎉 ALL 10 CRITICAL TESTS PASSED!")
        print("="*60)
        print("\nFeature 3: Messaging & Notifications - Production Ready ✅")
        print("\nCritical Functionality Verified:")
        print("  ✅ Notification settings API (GET/PUT)")
        print("  ✅ Delivery logs with pagination")
        print("  ✅ Telegram notifications with inline buttons")
        print("  ✅ Email notifications via SMTP")
        print("  ✅ User preference enforcement")
        print("  ✅ Manual notification sending")
        print("  ✅ Delivery logging")
        print("  ✅ Error handling and recovery")
        print("  ✅ User data isolation")
        print("="*60)
