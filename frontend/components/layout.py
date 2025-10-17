"""Layout components for the application."""

import streamlit as st


def render_header(title: str, subtitle: str = ""):
    """Render page header."""
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.markdown("---")


def render_sidebar():
    """Render sidebar with navigation and user info."""
    with st.sidebar:
        st.markdown("## Navigation")
        
        if st.session_state.get("authenticated", False):
            st.success(f"Logged in as: {st.session_state.get('user_email', 'User')}")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.session_state.access_token = None
                st.rerun()
        else:
            st.warning("Not logged in")


def render_footer():
    """Render footer."""
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: gray; padding: 1rem;">'
        'LinkedIn Ghostwriter © 2025 | Powered by AI'
        '</div>',
        unsafe_allow_html=True
    )


def require_auth():
    """Require authentication for a page."""
    if not st.session_state.get("authenticated", False):
        st.warning("🔒 You need to be logged in to access this page.")
        st.info("Please navigate to the Login page from the sidebar.")
        st.stop()
