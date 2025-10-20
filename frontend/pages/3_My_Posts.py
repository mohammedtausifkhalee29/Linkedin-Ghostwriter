"""My Posts Page - Post history and management."""

import streamlit as st
import asyncio
from datetime import datetime
from components.layout import render_header, require_auth
from utils.api_client import APIClient

# Page config
st.set_page_config(page_title="My Posts", page_icon="📚", layout="wide")

# Require authentication
require_auth()

# Render header
render_header("📚 My Posts", "View and manage your post history")

# Initialize API client
api_client = APIClient()


# Helper functions
async def load_posts(status_filter=None):
    """Load posts from API with optional status filter."""
    try:
        # Convert "All" to None for API call
        filter_value = None if status_filter == "All" else status_filter.lower() if status_filter else None
        
        posts = await api_client.get_posts(
            token=st.session_state.access_token,
            skip=0,
            limit=100,
            status_filter=filter_value
        )
        return posts
    except Exception as e:
        st.error(f"Failed to load posts: {str(e)}")
        return []


async def load_delivery_logs():
    """Load delivery logs for posts."""
    try:
        logs_data = await api_client.get_delivery_logs(
            token=st.session_state.access_token,
            page=1,
            limit=100
        )
        return logs_data.get("logs", [])
    except Exception as e:
        return []


async def retry_send_post(post_id, channel):
    """Retry sending a failed post."""
    try:
        result = await api_client.send_post_notification(
            token=st.session_state.access_token,
            post_id=post_id,
            channel=channel
        )
        return result
    except Exception as e:
        st.error(f"Failed to retry: {str(e)}")
        return None


async def publish_draft_post(post_id):
    """Publish a draft post."""
    try:
        result = await api_client.publish_draft(
            token=st.session_state.access_token,
            post_id=post_id
        )
        return result
    except Exception as e:
        st.error(f"Failed to publish draft: {str(e)}")
        return None


async def delete_post_by_id(post_id):
    """Delete a post."""
    try:
        await api_client.delete_post(
            token=st.session_state.access_token,
            post_id=post_id
        )
        return True
    except Exception as e:
        st.error(f"Failed to delete post: {str(e)}")
        return False


def get_delivery_status_for_post(post_id, delivery_logs):
    """Get the latest delivery status for a post."""
    post_logs = [log for log in delivery_logs if log.get("post_id") == post_id]
    
    if not post_logs:
        return None
    
    # Sort by created_at descending to get latest
    sorted_logs = sorted(
        post_logs,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    
    return sorted_logs


def render_delivery_status(post_id, delivery_logs):
    """Render delivery status indicators for a post."""
    statuses = get_delivery_status_for_post(post_id, delivery_logs)
    
    if not statuses:
        return
    
    st.markdown("**Delivery Status:**")
    
    for log in statuses[:3]:  # Show last 3 attempts
        channel = log.get("channel", "unknown")
        status = log.get("status", "unknown")
        created_at = log.get("created_at", "")
        error_msg = log.get("error_message", "")
        
        # Status icons
        if status == "delivered":
            status_icon = "✅"
            status_color = "green"
        elif status == "failed":
            status_icon = "❌"
            status_color = "red"
        elif status == "retried":
            status_icon = "🔄"
            status_color = "orange"
        else:
            status_icon = "❓"
            status_color = "gray"
        
        channel_icon = "✉️" if channel == "email" else "✈️"
        
        # Format timestamp
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_str = dt.strftime("%b %d, %I:%M %p")
            except:
                time_str = created_at[:16]
        else:
            time_str = ""
        
        # Display status
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            st.markdown(f"{status_icon} {channel_icon}")
        with col2:
            st.markdown(f"**{status.title()}**")
            if error_msg:
                st.caption(f"Error: {error_msg[:50]}...")
        with col3:
            st.caption(time_str)
            
            # Retry button for failed deliveries
            if status == "failed":
                if st.button("🔄 Retry", key=f"retry_{post_id}_{channel}_{created_at}"):
                    result = asyncio.run(retry_send_post(post_id, channel))
                    if result:
                        st.success(f"Retry queued for {channel}!")
                        st.rerun()

# Filters
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    search_query = st.text_input("🔍 Search posts", placeholder="Search by content...")

with col2:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Draft", "Published"]
    )

with col3:
    sort_by = st.selectbox(
        "Sort by",
        ["Newest", "Oldest"]
    )

# Load data
posts = asyncio.run(load_posts(status_filter))
delivery_logs = asyncio.run(load_delivery_logs())

# Apply search filter
if search_query:
    posts = [p for p in posts if search_query.lower() in p.get("content", "").lower()]

# Sort posts
if sort_by == "Newest":
    posts = sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)
else:
    posts = sorted(posts, key=lambda x: x.get("created_at", ""))

# Display posts
if not posts:
    st.info("📝 No posts yet. Start creating your first post!")
else:
    st.markdown(f"**{len(posts)} posts found**")
    st.markdown("---")
    
    for post in posts:
        post_id = post.get("id")
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Post preview
                st.markdown(f"**Post #{post_id}**")
                preview = post['content'][:150] + "..." if len(post['content']) > 150 else post['content']
                st.markdown(f"_{preview}_")
                
                # Metadata
                mode_badge = "🤖 Auto" if post['generation_mode'] == "auto" else "✨ Manual"
                status_badge = "📌 Published" if post.get('status') == "published" else "📋 Draft"
                created_date = datetime.fromisoformat(post['created_at']).strftime("%B %d, %Y at %I:%M %p")
                
                # Show template info for auto-generated posts
                template_info = ""
                if post.get('template_id'):
                    template_info = f" • 📝 Template #{post['template_id']}"
                
                st.caption(f"{mode_badge} • {status_badge}{template_info} • {created_date}")
                
                # Delivery status
                if delivery_logs:
                    render_delivery_status(post_id, delivery_logs)
            
            with col2:
                # Actions
                if st.button("👁️ View", key=f"view_{post_id}", use_container_width=True):
                    st.session_state[f"show_post_{post_id}"] = True
                
                if st.button("📋 Copy", key=f"copy_{post_id}", use_container_width=True):
                    st.toast("Copied to clipboard!")
                
                # Show "Publish" button for drafts, "Send" for published
                if post.get('status') == "draft":
                    if st.button("📤 Publish", key=f"publish_{post_id}", use_container_width=True, type="primary"):
                        result = asyncio.run(publish_draft_post(post_id))
                        if result:
                            st.success("✅ Post published!")
                            st.rerun()
                else:
                    if st.button("📱 Send", key=f"send_{post_id}", use_container_width=True):
                        st.session_state[f"send_post_{post_id}"] = True
                
                # Delete button
                if st.button("🗑️ Delete", key=f"delete_{post_id}", use_container_width=True):
                    if st.session_state.get(f"confirm_delete_{post_id}", False):
                        result = asyncio.run(delete_post_by_id(post_id))
                        if result:
                            st.success("✅ Post deleted!")
                            st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{post_id}"] = True
                        st.warning("⚠️ Click again to confirm")
                        st.rerun()
            
            # Full post view (expandable)
            if st.session_state.get(f"show_post_{post_id}", False):
                with st.expander("Full Post", expanded=True):
                    st.markdown(post['content'])
                    if st.button("Close", key=f"close_{post_id}"):
                        st.session_state[f"show_post_{post_id}"] = False
                        st.rerun()
            
            # Send dialog
            if st.session_state.get(f"send_post_{post_id}", False):
                with st.expander("Send Post", expanded=True):
                    channel = st.radio(
                        "Select delivery channel",
                        ["telegram", "email"],
                        format_func=lambda x: "✈️ Telegram" if x == "telegram" else "✉️ Email",
                        key=f"channel_{post_id}"
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Send", key=f"confirm_send_{post_id}", type="primary"):
                            result = asyncio.run(
                                api_client.send_post_notification(
                                    token=st.session_state.access_token,
                                    post_id=post_id,
                                    channel=channel
                                )
                            )
                            if result:
                                st.success(f"✅ Queued for {channel}!")
                                st.session_state[f"send_post_{post_id}"] = False
                                st.rerun()
                    with col_b:
                        if st.button("Cancel", key=f"cancel_send_{post_id}"):
                            st.session_state[f"send_post_{post_id}"] = False
                            st.rerun()
            
            st.markdown("---")


# Statistics
with st.sidebar:
    st.markdown("### 📊 Statistics")
    total_posts = len(posts) if posts else 0
    draft_posts = len([p for p in posts if p.get("status") == "draft"]) if posts else 0
    published_posts = len([p for p in posts if p.get("status") == "published"]) if posts else 0
    
    st.metric("Total Posts", total_posts)
    st.metric("Drafts", draft_posts)
    st.metric("Published", published_posts)
    
    # Delivery stats
    if delivery_logs:
        delivered_count = len([l for l in delivery_logs if l.get("status") == "delivered"])
        failed_count = len([l for l in delivery_logs if l.get("status") == "failed"])
        
        st.markdown("### 📬 Delivery Stats")
        st.metric("Delivered", delivered_count)
        st.metric("Failed", failed_count)
