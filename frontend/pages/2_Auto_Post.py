"""Auto Post Page - Template-based post generation."""

import streamlit as st
from components.layout import render_header, require_auth
from utils.api_client import APIClient

# Page config
st.set_page_config(page_title="Auto Post", page_icon="🤖", layout="wide")

# Require authentication
require_auth()

# Render header
render_header("🤖 Auto Post", "Use templates for quick post generation")

# Initialize API client
api_client = APIClient()

# Template selection
st.markdown("### 📝 Select a Template")

# Placeholder templates (will be fetched from API)
template_categories = {
    "Case Study": [
        {"id": 1, "name": "Problem-Solution-Results", "structure": "Hook → Problem → Solution → Results → CTA"},
        {"id": 2, "name": "Before-After", "structure": "Hook → Before State → Action Taken → After State → Lesson"}
    ],
    "Build in Public": [
        {"id": 3, "name": "Progress Update", "structure": "Hook → What I Built → Challenges → Learnings → Next Steps"},
        {"id": 4, "name": "Milestone Celebration", "structure": "Hook → Achievement → Journey → Gratitude → Future Goals"}
    ],
    "Personal Story": [
        {"id": 5, "name": "Career Journey", "structure": "Hook → Starting Point → Turning Point → Growth → Lesson"},
        {"id": 6, "name": "Lesson Learned", "structure": "Hook → Experience → Mistake → Insight → Application"}
    ]
}

# Category selection
selected_category = st.selectbox(
    "Category",
    options=list(template_categories.keys())
)

# Template selection within category
templates = template_categories[selected_category]
selected_template = st.selectbox(
    "Template",
    options=[t["name"] for t in templates],
    format_func=lambda x: f"{x}"
)

# Display template structure
template_data = next(t for t in templates if t["name"] == selected_template)
st.info(f"**Structure:** {template_data['structure']}")

# Input form
st.markdown("### ✍️ Provide Your Content")

with st.form("auto_post_form"):
    message = st.text_area(
        "Main Topic/Message",
        placeholder="What's the core topic or message for this post?",
        height=150,
        help="Provide the key information for your post"
    )
    
    references = st.text_area(
        "Additional Details (Optional)",
        placeholder="Any specific details, data points, or examples...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox(
            "Tone",
            ["Professional", "Casual", "Inspirational", "Educational"]
        )
    
    with col2:
        # Placeholder for length
        post_length = st.selectbox(
            "Post Length",
            ["Short (500 chars)", "Medium (1000 chars)", "Long (1500 chars)"]
        )
    
    submitted = st.form_submit_button("🚀 Generate Post", use_container_width=True, type="primary")

# Handle form submission
if submitted:
    if not message:
        st.error("Please provide a main topic or message.")
    else:
        with st.spinner("Generating your post from template..."):
            try:
                # TODO: Implement actual API call with template_id
                st.success(f"Post generated using '{selected_template}' template!")
                
                # Placeholder for generated post
                st.markdown("### 📝 Generated Post")
                st.info("Template-based post generation is not yet implemented. This is a placeholder.")
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("📋 Copy", use_container_width=True):
                        st.toast("Copied!")
                with col2:
                    if st.button("🔄 Regenerate", use_container_width=True):
                        st.toast("Regenerating...")
                with col3:
                    if st.button("📱 Telegram", use_container_width=True):
                        st.toast("Sent to Telegram!")
                with col4:
                    if st.button("📧 Email", use_container_width=True):
                        st.toast("Sent via email!")
                        
            except Exception as e:
                st.error(f"Error generating post: {str(e)}")

# Template info
with st.expander("ℹ️ About Templates"):
    st.markdown("""
    Templates provide a structured approach to post generation:
    
    - **Consistent Structure**: Follow proven post formats
    - **Faster Creation**: Just fill in your content
    - **Better Engagement**: Use formats that work
    - **Easy Customization**: AI adapts templates to your voice
    """)
