

 ### Feature 3: Messaging & Notifications
### Feature Name

Messaging & Notifications

### Feature Description

This feature enables automated delivery of generated LinkedIn posts to users via Telegram and email, along with daily posting reminders and error notifications. It ensures users can instantly access, review, and manage their AI-generated posts across channels they already use. The goal is to streamline workflow and maintain daily content consistency for professionals, founders, and creators without requiring manual copying or downloads.

### User Stories

As a user, I want to receive my AI-generated LinkedIn post directly on Telegram, so I can review or approve it quickly before publishing.
As a user, I want to get the generated post in my inbox, formatted and ready to post, so I can manage my drafts through email.
As a user, I want to receive daily reminders via Telegram or email to post new content, so I can stay consistent in my posting routine.
As a user, I want to get notified if post delivery fails and retry sending, so I never lose generated content.

### Acceptance Criteria

Telegram Bot sends generated post to user with inline actions: 👍 Approve | ♻️ Regenerate | 🗑️ Delete.
Email delivery uses SMTP/SendGrid and sends the formatted post with subject “Your LinkedIn Ghostwriter Post Draft.”
Optional daily reminders are configurable by time and channel (email/Telegram).
Delivery failures trigger error messages and retry options in the UI.
All messages and events are logged for monitoring.

### PRD Narrative

The Messaging & Notifications feature provides seamless delivery of generated posts via Telegram and email. Users can opt for daily reminders, automated notifications, and retry mechanisms. The integration prioritizes reliability, security, and simplicity. Telegram provides instant delivery with inline interactions, while email serves as a fallback and archival channel. This dual-channel approach ensures that users always have quick access to their content and stay consistent with their posting goals.

### Step-by-Step Developer Tasks

## Backend (FastAPI)

Telegram Integration


Configure Telegram Bot token and chat ID in .env.
Create /send-telegram endpoint:
Accepts payload: user_id, message, post_text.
Uses Telegram Bot API (python-telegram-bot or telebot library).
Sends message with inline buttons: Approve | Regenerate | Delete.
Create /telegram-callback endpoint to handle inline button actions.
Implement message logging (timestamp, status, user_id).
Email Integration


Configure SMTP (e.g., Gmail, SendGrid) credentials.
Create /send-email endpoint:
Accepts payload: to_email, subject, body.
Sends HTML-formatted post using smtplib or sendgrid.
Returns success/failure response with status code.
Implement email retry logic (max 3 attempts, exponential backoff).
Notification Scheduling


Integrate APScheduler or Celery for scheduled jobs.
Create scheduler service to send daily reminders:
Reads user preferences from config/database.
Sends reminder (“Time to post! Click to create your next post → [link]”).
Provide endpoint /update-reminder-settings.
Error Handling & Retry


Global error middleware to log and return structured error responses.
Retry logic for Telegram/email send failures with notification in Streamlit UI.
Store retry logs and timestamps.
Database/Logging


Table/JSON log structure:
 {
  "user_id": "123",
  "channel": "telegram/email",
  "post_id": "abc123",
  "status": "delivered/failed",
  "timestamp": "2025-10-18T10:45:00Z"
}


## Frontend (Streamlit)

Add Notifications Settings Page:
Options: Toggle email/Telegram delivery.
Configure daily reminder ON/OFF + time picker.
Display delivery logs (Delivered | Failed | Retried).
Add visual status updates after post send (e.g., “✅ Sent via Telegram”).
Show retry button if message delivery fails.
Display upcoming reminders and allow users to reschedule.

## Testing

Mock Telegram and SMTP APIs for integration tests.
Validate post delivery success and retry flow.
Simulate reminder scheduling and verify notifications trigger on time.
UI smoke test for settings and notification messages.

### Rules & Standards

## Design Principles

Simple, non-intrusive UI for delivery confirmations and reminders.
Emphasis on reliability and quick response (delivery within 3s for Telegram).
Notifications should never block main app flow.
Default reminder time set to 9:00 AM local time.

## Coding Standards

Language: Python 3.11+
Frameworks: FastAPI, Streamlit, APScheduler, python-telegram-bot, smtplib/sendgrid.
Async endpoints for sending notifications.
Store message logs in /data/logs or database.
Maintain modular structure:
/routes/notifications.py
/services/messaging_service.py
/utils/email_client.py

## Formatting & Linting

Use black, flake8, isort.
Run pytest for all tests.
Enforce code review before merging changes.

## File Handling & Secrets

Telegram and email credentials stored in .env.
Do not log message content with PII.
Sanitize and escape HTML for email content.

## Security

Validate chat ID and recipient email before sending.
Apply rate limiting on notification endpoints.
HTTPS-only communication.

## Testing & QA

End-to-end tests for Telegram and email send flow.
Performance check: <3s delivery average.
Reminder accuracy: ±1 min tolerance.
Verify logs for completeness and integrity.

## Deliverables

FastAPI endpoints (/send-telegram, /send-email, /update-reminder-settings)
Streamlit notification settings page
APScheduler integration
Unit + integration test scripts
.env.example for credentials

