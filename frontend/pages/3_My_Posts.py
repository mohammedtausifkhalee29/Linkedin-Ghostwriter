"""My Posts Page - Post history and management."""

import streamlit as st
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

# Filters
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    search_query = st.text_input("🔍 Search posts", placeholder="Search by content...")

with col2:
    filter_mode = st.selectbox(
        "Filter by Mode",
        ["All", "Manual", "Auto"]
    )

with col3:
    sort_by = st.selectbox(
        "Sort by",
        ["Newest", "Oldest"]
    )

# Fetch posts
with st.spinner("Loading your posts..."):
    try:
        # TODO: Implement actual API call
        # posts = await api_client.get_posts(st.session_state.access_token)
        
        # Placeholder posts
        placeholder_posts = [
            {
                "id": 1,
                "content": "Just shipped a new feature! Here's what I learned about...",
                "generation_mode": "manual",
                "created_at": "2025-10-15T10:30:00",
                "template_id": None
            },
            {
                "id": 2,
                "content": "Celebrating 1 year of building in public! The journey has been...",
                "generation_mode": "auto",
                "created_at": "2025-10-14T15:20:00",
                "template_id": 4
            },
            {
                "id": 3,
                "content": "5 lessons I learned from my biggest failure in tech...",
                "generation_mode": "manual",
                "created_at": "2025-10-13T09:15:00",
                "template_id": None
            }
        ]
        
        # Display posts
        if not placeholder_posts:
            st.info("📝 No posts yet. Start creating your first post!")
        else:
            st.markdown(f"**{len(placeholder_posts)} posts found**")
            st.markdown("---")
            
            for post in placeholder_posts:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        # Post preview
                        st.markdown(f"**Post #{post['id']}**")
                        preview = post['content'][:150] + "..." if len(post['content']) > 150 else post['content']
                        st.markdown(f"_{preview}_")
                        
                        # Metadata
                        mode_badge = "🤖 Auto" if post['generation_mode'] == "auto" else "✨ Manual"
                        created_date = datetime.fromisoformat(post['created_at']).strftime("%B %d, %Y at %I:%M %p")
                        st.caption(f"{mode_badge} • {created_date}")
                    
                    with col2:
                        # Actions
                        if st.button("👁️ View", key=f"view_{post['id']}", use_container_width=True):
                            st.session_state[f"show_post_{post['id']}"] = True
                        
                        if st.button("📋 Copy", key=f"copy_{post['id']}", use_container_width=True):
                            st.toast("Copied to clipboard!")
                        
                        if st.button("📱 Send", key=f"send_{post['id']}", use_container_width=True):
                            st.session_state[f"send_post_{post['id']}"] = True
                    
                    # Full post view (expandable)
                    if st.session_state.get(f"show_post_{post['id']}", False):
                        with st.expander("Full Post", expanded=True):
                            st.markdown(post['content'])
                            if st.button("Close", key=f"close_{post['id']}"):
                                st.session_state[f"show_post_{post['id']}"] = False
                                st.rerun()
                    
                    # Send dialog
                    if st.session_state.get(f"send_post_{post['id']}", False):
                        with st.expander("Send Post", expanded=True):
                            channel = st.radio(
                                "Select delivery channel",
                                ["Telegram", "Email"],
                                key=f"channel_{post['id']}"
                            )
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("Send", key=f"confirm_send_{post['id']}", type="primary"):
                                    st.toast(f"Sent via {channel}!")
                                    st.session_state[f"send_post_{post['id']}"] = False
                                    st.rerun()
                            with col_b:
                                if st.button("Cancel", key=f"cancel_send_{post['id']}"):
                                    st.session_state[f"send_post_{post['id']}"] = False
                                    st.rerun()
                    
                    st.markdown("---")
        
    except Exception as e:
        st.error(f"Error loading posts: {str(e)}")

# Statistics
with st.sidebar:
    st.markdown("### 📊 Statistics")
    st.metric("Total Posts", "3")
    st.metric("This Week", "2")
    st.metric("This Month", "8")
