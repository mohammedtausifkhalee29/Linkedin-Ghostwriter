"""Create Post Page - Manual post generation."""

import streamlit as st
from components.layout import render_header, require_auth
from utils.api_client import APIClient

# Page config
st.set_page_config(page_title="Create Post", page_icon="✨", layout="wide")

# Require authentication
require_auth()

# Render header
render_header("✨ Create Post", "Generate custom LinkedIn posts with AI")

# Initialize API client
api_client = APIClient()

# Main form
with st.form("create_post_form"):
    st.markdown("### Post Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        post_type = st.selectbox(
            "Post Type",
            ["Case Study", "Build in Public", "Personal Story", "Tips & Advice", "Industry Insights"]
        )
        
        tone = st.selectbox(
            "Tone",
            ["Professional", "Casual", "Inspirational", "Educational", "Humorous"]
        )
    
    with col2:
        # Placeholder for additional options
        st.markdown("**Additional Options**")
        include_hashtags = st.checkbox("Include hashtags", value=True)
        include_cta = st.checkbox("Include call-to-action", value=True)
    
    st.markdown("### Content")
    
    message = st.text_area(
        "Main Message",
        placeholder="What do you want to share with your audience?",
        height=150,
        help="Provide the core message or topic for your post"
    )
    
    references = st.text_area(
        "References (Optional)",
        placeholder="Add any reference materials, links, or examples...",
        height=100
    )
    
    additional_context = st.text_input(
        "Additional Context (Optional)",
        placeholder="Any specific requirements or context..."
    )
    
    # File upload (placeholder for future implementation)
    uploaded_file = st.file_uploader(
        "Upload Reference Document (Optional)",
        type=["txt", "pdf", "docx"],
        help="Upload a document for additional context"
    )
    
    submitted = st.form_submit_button("🎯 Generate Post", use_container_width=True, type="primary")

# Handle form submission
if submitted:
    if not message:
        st.error("Please provide a main message for your post.")
    else:
        with st.spinner("Generating your post..."):
            try:
                # TODO: Implement actual API call
                st.success("Post generated successfully!")
                
                # Placeholder for generated post
                st.markdown("### 📝 Generated Post")
                st.info("Post generation is not yet implemented. This is a placeholder.")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                        st.toast("Copied to clipboard!")
                with col2:
                    if st.button("📱 Send to Telegram", use_container_width=True):
                        st.toast("Sent to Telegram!")
                with col3:
                    if st.button("📧 Send via Email", use_container_width=True):
                        st.toast("Sent via email!")
                        
            except Exception as e:
                st.error(f"Error generating post: {str(e)}")

# Tips section
with st.expander("💡 Tips for Better Posts"):
    st.markdown("""
    - **Be specific**: Provide clear details about what you want to communicate
    - **Add context**: Include relevant examples or references
    - **Choose the right tone**: Match the tone to your audience and message
    - **Review and edit**: AI-generated posts are a starting point - personalize them!
    """)
