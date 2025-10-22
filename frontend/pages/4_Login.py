"""Login Page - User authentication."""

import streamlit as st
import asyncio
from utils.api_client import APIClient

# Page config
st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .login-header {
        text-align: center;
        padding: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="login-header"><h1>🔐 LinkedIn Ghostwriter</h1></div>', unsafe_allow_html=True)

# Initialize API client
api_client = APIClient()

# Check if already logged in
if st.session_state.get("authenticated", False):
    st.success(f"✅ Already logged in as {st.session_state.get('user_email')}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Go to Home", use_container_width=True):
            st.switch_page("app.py")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.access_token = None
            st.rerun()
    st.stop()

# Tabs for login and register
tab1, tab2 = st.tabs(["Login", "Register"])

# Login tab
with tab1:
    st.markdown("### Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        remember_me = st.checkbox("Remember me")
        
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
    
    if submitted:
        if not email or not password:
            st.error("Please provide both email and password.")
        else:
            with st.spinner("Logging in..."):
                try:
                    # Call the actual API
                    result = asyncio.run(api_client.login(email, password))
                    
                    # Store authentication data
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.access_token = result.get("access_token")
                    st.session_state.token = result.get("access_token")  # Some pages use 'token'
                    
                    st.success("Login successful!")
                    st.balloons()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
                    st.info("💡 Tip: Make sure you have registered an account first, or check if the backend server is running.")

# Register tab
with tab2:
    st.markdown("### Create a New Account")
    
    with st.form("register_form"):
        reg_email = st.text_input("Email", placeholder="your.email@example.com", key="reg_email")
        reg_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        accept_terms = st.checkbox("I accept the Terms of Service and Privacy Policy")
        
        submitted = st.form_submit_button("Register", use_container_width=True, type="primary")
    
    if submitted:
        if not reg_email or not reg_password or not reg_confirm:
            st.error("Please fill in all fields.")
        elif reg_password != reg_confirm:
            st.error("Passwords do not match.")
        elif len(reg_password) < 6:
            st.error("Password must be at least 6 characters long.")
        elif not accept_terms:
            st.error("Please accept the Terms of Service.")
        else:
            with st.spinner("Creating your account..."):
                try:
                    # Call the actual API
                    result = asyncio.run(api_client.register(reg_email, reg_password))
                    
                    st.success("Account created successfully! Please login with your credentials.")
                    st.balloons()
                    
                except Exception as e:
                    error_msg = str(e)
                    if "400" in error_msg:
                        st.error("Registration failed: Email already exists or invalid data.")
                    else:
                        st.error(f"Registration failed: {error_msg}")
                    st.info("💡 Tip: Make sure the backend server is running.")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: gray;">'
    'Need help? Contact support@example.com'
    '</div>',
    unsafe_allow_html=True
)
