"""LinkedIn Ghostwriter - Streamlit Frontend Application."""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="LinkedIn Ghostwriter",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""
    
    st.markdown('<h1 class="main-header">✍️ LinkedIn Ghostwriter</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Check authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.warning("👋 Please login to access the application.")
        st.info("Navigate to the **Login** page from the sidebar.")
    else:
        st.success(f"Welcome back, {st.session_state.get('user_email', 'User')}!")
        
        st.markdown("### 🚀 Quick Start")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### ✨ Create Post")
            st.markdown("Generate custom LinkedIn posts with AI")
            if st.button("Go to Create Post", key="nav_create"):
                st.switch_page("pages/1_Create_Post.py")
        
        with col2:
            st.markdown("#### 🤖 Auto Post")
            st.markdown("Use templates for quick post generation")
            if st.button("Go to Auto Post", key="nav_auto"):
                st.switch_page("pages/2_Auto_Post.py")
        
        with col3:
            st.markdown("#### 📚 My Posts")
            st.markdown("View your post history")
            if st.button("Go to My Posts", key="nav_history"):
                st.switch_page("pages/3_My_Posts.py")
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.markdown("""
        This AI-powered tool helps you create engaging LinkedIn posts effortlessly.
        
        **Features:**
        - 🎯 Custom post generation with AI
        - 📝 Template-based auto posting
        - 💾 Post history tracking
        - 📱 Telegram & email delivery
        """)


if __name__ == "__main__":
    main()
