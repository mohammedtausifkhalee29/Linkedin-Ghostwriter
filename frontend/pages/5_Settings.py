"""Notification Settings Page for LinkedIn Ghostwriter."""

import streamlit as st
import asyncio
from datetime import time

from components.layout import apply_custom_css
from utils.api_client import APIClient

# Initialize API client
api_client = APIClient()

# Apply custom styling
apply_custom_css()

# Page configuration
st.title("⚙️ Notification Settings")
st.markdown("Configure how and when you receive notifications for generated posts.")

# Check authentication
if "access_token" not in st.session_state or not st.session_state.access_token:
    st.warning("⚠️ Please login to access settings.")
    if st.button("Go to Login"):
        st.switch_page("pages/4_Login.py")
    st.stop()

# Load settings function
async def load_settings():
    """Load user's notification settings from API."""
    try:
        settings = await api_client.get_notification_settings(st.session_state.access_token)
        return settings
    except Exception as e:
        st.error(f"Failed to load settings: {str(e)}")
        return None

# Update settings function
async def update_settings(data):
    """Update user's notification settings."""
    try:
        result = await api_client.update_notification_settings(
            token=st.session_state.access_token,
            **data
        )
        return result
    except Exception as e:
        st.error(f"Failed to update settings: {str(e)}")
        return None

# Load delivery logs
async def load_delivery_logs(page=1):
    """Load delivery logs with pagination."""
    try:
        logs = await api_client.get_delivery_logs(
            token=st.session_state.access_token,
            page=page,
            limit=20
        )
        return logs
    except Exception as e:
        st.error(f"Failed to load delivery logs: {str(e)}")
        return None

# Initialize session state for settings
if "notification_settings" not in st.session_state:
    st.session_state.notification_settings = asyncio.run(load_settings())

# Display settings form
if st.session_state.notification_settings:
    settings = st.session_state.notification_settings
    
    st.markdown("---")
    st.subheader("📬 Notification Channels")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_enabled = st.checkbox(
            "✉️ Email Notifications",
            value=settings.get("receive_email_notifications", True),
            help="Receive generated posts via email"
        )
    
    with col2:
        telegram_enabled = st.checkbox(
            "✈️ Telegram Notifications",
            value=settings.get("receive_telegram_notifications", True),
            help="Receive generated posts via Telegram"
        )
    
    st.markdown("---")
    st.subheader("🔗 Telegram Configuration")
    
    telegram_chat_id = st.text_input(
        "Telegram Chat ID",
        value=st.session_state.get("user_telegram_chat_id", ""),
        placeholder="Enter your Telegram chat ID",
        help="Get your chat ID by messaging @userinfobot on Telegram"
    )
    
    if telegram_chat_id:
        st.info(f"💬 Chat ID: `{telegram_chat_id}`")
    else:
        st.warning("⚠️ Please set your Telegram Chat ID to receive Telegram notifications.")
    
    st.markdown("---")
    st.subheader("🔔 Daily Reminders")
    
    reminder_enabled = st.toggle(
        "Enable Daily Reminders",
        value=settings.get("daily_reminder_enabled", False),
        help="Receive a daily reminder to create new content"
    )
    
    if reminder_enabled:
        # Parse existing reminder time
        reminder_time_str = settings.get("daily_reminder_time", "09:00:00")
        try:
            if isinstance(reminder_time_str, str):
                hour, minute = map(int, reminder_time_str.split(":")[0:2])
            else:
                hour, minute = 9, 0
        except:
            hour, minute = 9, 0
        
        reminder_time = st.time_input(
            "Reminder Time",
            value=time(hour, minute),
            help="Time to receive daily reminder (your local time)"
        )
        
        st.info(f"⏰ You will receive reminders at {reminder_time.strftime('%I:%M %p')} daily.")
    else:
        reminder_time = time(9, 0)  # Default
    
    st.markdown("---")
    
    # Save button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save Settings", use_container_width=True, type="primary"):
            # Prepare update data
            update_data = {
                "receive_email_notifications": email_enabled,
                "receive_telegram_notifications": telegram_enabled,
                "daily_reminder_enabled": reminder_enabled,
                "daily_reminder_time": f"{reminder_time.hour:02d}:{reminder_time.minute:02d}:00"
            }
            
            if telegram_chat_id:
                update_data["telegram_chat_id"] = telegram_chat_id
                st.session_state.user_telegram_chat_id = telegram_chat_id
            
            # Update settings
            result = asyncio.run(update_settings(update_data))
            
            if result:
                st.success("✅ Settings saved successfully!")
                st.session_state.notification_settings = result
                st.rerun()
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.notification_settings = asyncio.run(load_settings())
            st.rerun()
    
    st.markdown("---")
    st.subheader("📊 Delivery Logs")
    st.markdown("View the history of notification deliveries")
    
    # Load and display delivery logs
    logs_data = asyncio.run(load_delivery_logs())
    
    if logs_data and logs_data.get("logs"):
        logs = logs_data["logs"]
        total = logs_data.get("total", 0)
        
        st.caption(f"Showing {len(logs)} of {total} total delivery logs")
        
        # Display logs in a table
        for log in logs:
            status_icon = "✅" if log["status"] == "delivered" else "❌" if log["status"] == "failed" else "🔄"
            channel_icon = "✉️" if log["channel"] == "email" else "✈️"
            
            col1, col2, col3, col4 = st.columns([1, 2, 2, 4])
            
            with col1:
                st.markdown(f"{status_icon} {channel_icon}")
            
            with col2:
                st.markdown(f"**{log['status'].title()}**")
            
            with col3:
                created_at = log.get("created_at", "")
                if created_at:
                    st.markdown(f"_{created_at[:16]}_")
            
            with col4:
                if log.get("error_message"):
                    st.markdown(f"Error: {log['error_message']}")
                elif log.get("post_id"):
                    st.markdown(f"Post ID: {log['post_id']}")
                else:
                    st.markdown("Daily reminder")
            
            st.divider()
        
        # Pagination controls
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=max(1, (total + 19) // 20),
                value=1,
                step=1
            )
            if st.button("Load Page"):
                logs_data = asyncio.run(load_delivery_logs(page))
                st.rerun()
    else:
        st.info("📭 No delivery logs yet. Generate and send a post to see logs here!")

else:
    st.error("Failed to load notification settings. Please try refreshing the page.")
    if st.button("🔄 Refresh"):
        st.session_state.notification_settings = asyncio.run(load_settings())
        st.rerun()

# Help section
st.markdown("---")
with st.expander("ℹ️ How to get your Telegram Chat ID"):
    st.markdown("""
    1. Open Telegram and search for **@userinfobot**
    2. Start a conversation with the bot by clicking 'Start'
    3. The bot will send you your Chat ID
    4. Copy the Chat ID and paste it in the field above
    5. Save your settings
    
    Once configured, you'll receive your generated LinkedIn posts directly in Telegram!
    """)

with st.expander("ℹ️ Email Configuration"):
    st.markdown("""
    Email notifications are sent to the email address associated with your account.
    
    **Email Format:**
    - Subject: "Your LinkedIn Ghostwriter Post Draft"
    - Body: Formatted post content ready to copy and paste to LinkedIn
    
    Make sure to check your spam folder if you don't see the emails.
    """)

with st.expander("ℹ️ Daily Reminders"):
    st.markdown("""
    Enable daily reminders to stay consistent with your LinkedIn posting schedule.
    
    **How it works:**
    - Choose your preferred reminder time
    - Receive a daily notification at the specified time
    - Reminders are sent via your enabled channels (Telegram or Email)
    - Helps you maintain a consistent posting routine
    """)
