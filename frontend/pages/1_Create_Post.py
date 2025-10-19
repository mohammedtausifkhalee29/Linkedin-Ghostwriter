"""Create Post Page - Manual post generation."""

import streamlit as st
import asyncio
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

# Initialize session state
if "generated_post" not in st.session_state:
    st.session_state.generated_post = None
if "post_id" not in st.session_state:
    st.session_state.post_id = None

# Post Type Options
POST_TYPES = [
    "Case Study",
    "Motivational",
    "How-To",
    "Personal Story",
    "Industry Insights",
    "Lessons Learned",
    "Behind the Scenes"
]

# Tone Options
TONE_OPTIONS = [
    "Professional",
    "Casual",
    "Inspirational",
    "Educational",
    "Humorous",
    "Thought-Provoking"
]

# Main form
with st.form("create_post_form", clear_on_submit=False):
    st.markdown("### 📋 Post Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        post_type = st.selectbox(
            "Post Type *",
            POST_TYPES,
            help="Select the type of LinkedIn post you want to create"
        )
        
        tone = st.selectbox(
            "Tone *",
            TONE_OPTIONS,
            help="Choose the tone for your post"
        )
    
    with col2:
        st.markdown("**Upload Reference Material (Optional)**")
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=["txt", "pdf", "md"],
            help="Upload a text file or PDF for reference (Max 10MB)",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
            st.caption(f"📎 {uploaded_file.name} ({file_size_mb:.2f} MB)")
    
    st.markdown("### ✍️ Your Message")
    
    message = st.text_area(
        "Main Message *",
        placeholder="What do you want to share? Be specific about your topic, experience, or insight...",
        height=150,
        help="Provide the core message or topic for your post (required)",
        max_chars=2000
    )
    
    st.markdown("### ⚙️ Additional Options")
    
    col_a, col_b = st.columns(2)
    with col_a:
        include_emoji = st.checkbox("Include emojis", value=True)
    with col_b:
        include_cta = st.checkbox("Include call-to-action", value=True)
    
    # Submit button
    submitted = st.form_submit_button(
        "🎯 Generate Post",
        use_container_width=True,
        type="primary"
    )

# Handle form submission
if submitted:
    if not message or len(message.strip()) < 10:
        st.error("⚠️ Please provide a meaningful message (at least 10 characters)")
    else:
        # Extract reference text from uploaded file
        reference_text = None
        
        if uploaded_file is not None:
            try:
                with st.spinner("📄 Processing uploaded file..."):
                    file_content = uploaded_file.getvalue()
                    
                    # For now, handle text files directly
                    # PDF processing will be done by backend
                    if uploaded_file.name.lower().endswith(('.txt', '.md')):
                        reference_text = file_content.decode('utf-8', errors='ignore')[:10000]
                    else:
                        # For PDFs, send to backend as is
                        reference_text = f"[PDF file: {uploaded_file.name}]"
                        st.info("📄 PDF file will be processed by the system")
                        
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                reference_text = None
        
        # Generate post
        with st.spinner("🤖 Generating your post... This may take a few seconds."):
            try:
                # Make API call using asyncio
                async def generate():
                    return await api_client.generate_post(
                        token=st.session_state.access_token,
                        post_type=post_type,
                        message=message,
                        tone=tone,
                        reference_text=reference_text
                    )
                
                result = asyncio.run(generate())
                
                if result and "post" in result:
                    st.session_state.generated_post = result["post"]["content"]
                    st.session_state.post_id = result["post"].get("id")
                    st.success("✅ Post generated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate post. Please try again.")
                    
            except Exception as e:
                st.error(f"❌ Error generating post: {str(e)}")
                st.info("💡 Tip: Make sure your backend server is running and your API token is valid.")

# Display generated post
if st.session_state.generated_post:
    st.markdown("---")
    st.markdown("### 📝 Generated Post")
    
    # Display post in a nice box
    st.markdown(
        f"""
        <div style="
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #0066cc;
            margin: 10px 0;
        ">
        {st.session_state.generated_post.replace(chr(10), '<br>')}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Character count
    char_count = len(st.session_state.generated_post)
    st.caption(f"📊 Character count: {char_count}")
    
    # Action buttons
    st.markdown("### 🎬 Actions")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("📋 Copy", use_container_width=True):
            # Note: Actual clipboard copy requires JS, so we show instructions
            st.code(st.session_state.generated_post, language=None)
            st.info("👆 Select and copy the text above")
    
    with col2:
        if st.button("� Regenerate", use_container_width=True):
            st.session_state.generated_post = None
            st.session_state.post_id = None
            st.rerun()
    
    with col3:
        if st.button("💾 Save Draft", use_container_width=True):
            with st.spinner("Saving draft..."):
                try:
                    async def save_draft():
                        return await api_client.save_draft(
                            token=st.session_state.access_token,
                            content=st.session_state.generated_post,
                            reference_text=reference_text if 'reference_text' in locals() else None
                        )
                    
                    result = asyncio.run(save_draft())
                    if result and result.get("status") == "success":
                        st.success("✅ Draft saved successfully!")
                    else:
                        st.error("❌ Failed to save draft")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col4:
        if st.button("📱 Send to Telegram", use_container_width=True):
            with st.spinner("Sending to Telegram..."):
                try:
                    async def send_telegram():
                        return await api_client.send_post(
                            token=st.session_state.access_token,
                            post_content=st.session_state.generated_post,
                            channel="telegram"
                        )
                    
                    result = asyncio.run(send_telegram())
                    if result and result.get("status") == "success":
                        st.success("✅ Sent to Telegram!")
                    else:
                        st.error("❌ Failed to send to Telegram")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col5:
        if st.button("📧 Send via Email", use_container_width=True):
            with st.spinner("Sending via email..."):
                try:
                    async def send_email():
                        return await api_client.send_post(
                            token=st.session_state.access_token,
                            post_content=st.session_state.generated_post,
                            channel="email"
                        )
                    
                    result = asyncio.run(send_email())
                    if result and result.get("status") == "success":
                        st.success("✅ Sent via email!")
                    else:
                        st.error("❌ Failed to send via email")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Edit option
    with st.expander("✏️ Edit Post"):
        edited_content = st.text_area(
            "Edit your post",
            value=st.session_state.generated_post,
            height=300,
            key="edit_post_area"
        )
        
        if st.button("💾 Save Changes", key="save_edit"):
            st.session_state.generated_post = edited_content
            st.success("✅ Changes saved!")
            st.rerun()

# Tips section
with st.expander("💡 Tips for Better Posts"):
    st.markdown("""
    ### Creating Engaging LinkedIn Posts
    
    **Be Specific**
    - Provide clear details about what you want to communicate
    - Use concrete examples rather than vague statements
    
    **Add Context**
    - Include relevant background information
    - Reference specific situations or experiences
    
    **Choose the Right Tone**
    - Match your tone to your audience and message
    - Consider your personal brand and industry
    
    **Use References**
    - Upload articles, reports, or notes to give the AI more context
    - The more specific information you provide, the better the output
    
    **Review and Personalize**
    - AI-generated posts are starting points
    - Always review and add your personal touch
    - Edit to match your authentic voice
    """)

# Footer
st.markdown("---")
st.caption("💡 Tip: Your best posts combine AI assistance with your unique perspective and voice.")
