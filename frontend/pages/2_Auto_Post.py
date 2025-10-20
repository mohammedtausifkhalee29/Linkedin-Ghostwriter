"""Auto Post Page - Template-based post generation."""

import streamlit as st
import asyncio
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

# Initialize session state
if "generated_post" not in st.session_state:
    st.session_state.generated_post = None
if "selected_template_data" not in st.session_state:
    st.session_state.selected_template_data = None
if "templates" not in st.session_state:
    st.session_state.templates = None

# Fetch templates from API
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_templates():
    """Fetch templates from API."""
    try:
        response = asyncio.run(api_client.get_templates())
        if response:
            # Group templates by category
            categories = {}
            for template in response:
                category = template.get("category", "Other")
                if category not in categories:
                    categories[category] = []
                categories[category].append(template)
            return categories
    except Exception as e:
        st.error(f"Failed to load templates: {str(e)}")
    return None

# Load templates
template_categories = fetch_templates()

if not template_categories:
    st.warning("No templates available. Please check your connection.")
    st.stop()

# Template selection
st.markdown("### 📝 Select a Template")
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
