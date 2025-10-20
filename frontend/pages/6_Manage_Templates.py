"""Template Management Page - Admin interface for managing templates."""

import streamlit as st
import asyncio
from typing import Optional
from utils.api_client import APIClient

# Initialize API client
api_client = APIClient()

st.set_page_config(page_title="Manage Templates", page_icon="📝", layout="wide")

# Check authentication
if "token" not in st.session_state or not st.session_state.token:
    st.warning("⚠️ Please log in first")
    st.switch_page("pages/4_Login.py")
    st.stop()

st.title("📝 Template Management")
st.markdown("Create, edit, and manage your LinkedIn post templates")

# Initialize session state for managing UI state
if "selected_template" not in st.session_state:
    st.session_state.selected_template = None
if "show_create_form" not in st.session_state:
    st.session_state.show_create_form = False
if "show_edit_form" not in st.session_state:
    st.session_state.show_edit_form = False
if "show_versions" not in st.session_state:
    st.session_state.show_versions = False


def reset_forms():
    """Reset all form states."""
    st.session_state.show_create_form = False
    st.session_state.show_edit_form = False
    st.session_state.show_versions = False
    st.session_state.selected_template = None


async def load_templates(category_filter: Optional[str] = None, tone_filter: Optional[str] = None, search: Optional[str] = None):
    """Load templates with optional filters."""
    try:
        result = await api_client.get_templates_filtered(
            token=st.session_state.token,
            category=category_filter,
            tone=tone_filter,
            search=search
        )
        return result.get("items", [])
    except Exception as e:
        st.error(f"❌ Error loading templates: {str(e)}")
        return []


async def load_template_stats():
    """Load template statistics."""
    try:
        return await api_client.get_template_stats(token=st.session_state.token)
    except Exception as e:
        st.error(f"❌ Error loading statistics: {str(e)}")
        return None


async def create_template(name: str, category: str, prompt: str, structure: str, tone: str, example: Optional[str]):
    """Create a new template."""
    try:
        result = await api_client.create_template(
            token=st.session_state.token,
            name=name,
            category=category,
            prompt=prompt,
            structure=structure,
            tone=tone,
            example=example
        )
        st.success(f"✅ Template '{name}' created successfully!")
        reset_forms()
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error creating template: {str(e)}")


async def update_template(template_id: int, name: Optional[str], category: Optional[str], prompt: Optional[str], 
                         structure: Optional[str], tone: Optional[str], example: Optional[str]):
    """Update an existing template."""
    try:
        result = await api_client.update_template(
            token=st.session_state.token,
            template_id=template_id,
            name=name,
            category=category,
            prompt=prompt,
            structure=structure,
            tone=tone,
            example=example
        )
        
        # Check if version was created
        new_version = result.get("current_version", 1)
        if new_version > 1:
            st.success(f"✅ Template updated! New version: v{new_version}")
        else:
            st.success("✅ Template metadata updated (no versioning needed)")
        
        reset_forms()
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error updating template: {str(e)}")


async def delete_template(template_id: int, template_name: str):
    """Delete a template."""
    try:
        await api_client.delete_template(token=st.session_state.token, template_id=template_id)
        st.success(f"✅ Template '{template_name}' deleted successfully!")
        reset_forms()
        st.rerun()
    except Exception as e:
        st.error(f"❌ Error deleting template: {str(e)}")


async def load_version_history(template_id: int):
    """Load version history for a template."""
    try:
        return await api_client.get_template_versions(
            token=st.session_state.token,
            template_id=template_id
        )
    except Exception as e:
        st.error(f"❌ Error loading version history: {str(e)}")
        return []


# Statistics Dashboard
st.subheader("📊 Template Statistics")
stats = asyncio.run(load_template_stats())

if stats:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Templates", stats.get("total_templates", 0))
    
    with col2:
        categories = stats.get("templates_by_category", {})
        st.metric("Categories", len(categories))
    
    with col3:
        tones = stats.get("templates_by_tone", {})
        st.metric("Tones", len(tones))
    
    with col4:
        most_used = stats.get("most_used_template", {})
        if most_used:
            st.metric("Most Used", most_used.get("name", "N/A"))

st.divider()

# Filters Section
st.subheader("🔍 Filter Templates")
col1, col2, col3, col4 = st.columns([2, 2, 3, 1])

with col1:
    category_filter = st.selectbox(
        "Category",
        options=["All", "Thought Leadership", "Personal Story", "Industry News", "Tutorial", "Career", "Achievement"],
        index=0
    )

with col2:
    tone_filter = st.selectbox(
        "Tone",
        options=["All", "Professional", "Conversational", "Casual", "Inspirational", "Reflective", "Honest"],
        index=0
    )

with col3:
    search_query = st.text_input("🔎 Search templates", placeholder="Search by name or structure...")

with col4:
    st.write("")  # Spacing
    st.write("")  # Spacing
    if st.button("➕ New Template", use_container_width=True):
        reset_forms()
        st.session_state.show_create_form = True
        st.rerun()

# Convert "All" to None for API
category_param = None if category_filter == "All" else category_filter
tone_param = None if tone_filter == "All" else tone_filter
search_param = search_query if search_query else None

# Load templates
templates = asyncio.run(load_templates(category_param, tone_param, search_param))

st.divider()

# Create Template Form
if st.session_state.show_create_form:
    st.subheader("➕ Create New Template")
    
    with st.form("create_template_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Template Name*", max_chars=100)
            new_category = st.selectbox(
                "Category*",
                options=["Thought Leadership", "Personal Story", "Industry News", "Tutorial", "Career", "Achievement"]
            )
            new_tone = st.selectbox(
                "Tone*",
                options=["Professional", "Conversational", "Casual", "Inspirational", "Reflective", "Honest"]
            )
        
        with col2:
            new_structure = st.text_area(
                "Structure*",
                placeholder="e.g., Hook + Main Point + CTA",
                height=100,
                max_chars=500
            )
            new_prompt = st.text_area(
                "AI Prompt*",
                placeholder="Instructions for AI to generate content...",
                height=100,
                max_chars=1000
            )
        
        new_example = st.text_area(
            "Example (Optional)",
            placeholder="Provide an example post using this template...",
            height=150
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit = st.form_submit_button("✅ Create", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit:
            if not all([new_name, new_category, new_prompt, new_structure, new_tone]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                asyncio.run(create_template(
                    name=new_name,
                    category=new_category,
                    prompt=new_prompt,
                    structure=new_structure,
                    tone=new_tone,
                    example=new_example if new_example else None
                ))
        
        if cancel:
            reset_forms()
            st.rerun()

# Edit Template Form
if st.session_state.show_edit_form and st.session_state.selected_template:
    template = st.session_state.selected_template
    st.subheader(f"✏️ Edit Template: {template['name']}")
    
    with st.form("edit_template_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            edit_name = st.text_input("Template Name*", value=template.get("name", ""), max_chars=100)
            edit_category = st.selectbox(
                "Category*",
                options=["Thought Leadership", "Personal Story", "Industry News", "Tutorial", "Career", "Achievement"],
                index=["Thought Leadership", "Personal Story", "Industry News", "Tutorial", "Career", "Achievement"].index(template.get("category", "Thought Leadership"))
            )
            edit_tone = st.selectbox(
                "Tone*",
                options=["Professional", "Conversational", "Casual", "Inspirational", "Reflective", "Honest"],
                index=["Professional", "Conversational", "Casual", "Inspirational", "Reflective", "Honest"].index(template.get("tone", "Professional"))
            )
        
        with col2:
            edit_structure = st.text_area(
                "Structure*",
                value=template.get("structure", ""),
                height=100,
                max_chars=500
            )
            edit_prompt = st.text_area(
                "AI Prompt*",
                value=template.get("prompt", ""),
                height=100,
                max_chars=1000
            )
        
        edit_example = st.text_area(
            "Example (Optional)",
            value=template.get("example", "") or "",
            height=150
        )
        
        st.info("💡 **Note:** Changing Prompt, Structure, or Tone will create a new version automatically.")
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            submit = st.form_submit_button("💾 Update", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit:
            if not all([edit_name, edit_category, edit_prompt, edit_structure, edit_tone]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                asyncio.run(update_template(
                    template_id=template["id"],
                    name=edit_name if edit_name != template.get("name") else None,
                    category=edit_category if edit_category != template.get("category") else None,
                    prompt=edit_prompt if edit_prompt != template.get("prompt") else None,
                    structure=edit_structure if edit_structure != template.get("structure") else None,
                    tone=edit_tone if edit_tone != template.get("tone") else None,
                    example=edit_example if edit_example != template.get("example") else None
                ))
        
        if cancel:
            reset_forms()
            st.rerun()

# Version History Modal
if st.session_state.show_versions and st.session_state.selected_template:
    template = st.session_state.selected_template
    st.subheader(f"📜 Version History: {template['name']}")
    
    versions = asyncio.run(load_version_history(template["id"]))
    
    if versions:
        for version in versions:
            with st.expander(f"Version {version['version']} - {version['created_at'][:10]}", expanded=(version['version'] == template.get('current_version'))):
                st.markdown(f"**Prompt:** {version['prompt']}")
                st.markdown(f"**Structure:** {version['structure']}")
                st.markdown(f"**Tone:** {version['tone']}")
                if version.get('example'):
                    st.markdown(f"**Example:**\n{version['example']}")
    else:
        st.info("No version history available")
    
    if st.button("❌ Close Version History"):
        st.session_state.show_versions = False
        st.rerun()

# Templates List
st.subheader(f"📋 Templates ({len(templates)})")

if not templates:
    st.info("No templates found. Create your first template!")
else:
    for template in templates:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### {template['name']}")
                st.markdown(f"**Category:** {template['category']} | **Tone:** {template['tone']} | **Version:** v{template.get('current_version', 1)}")
                
                with st.expander("View Details"):
                    st.markdown(f"**Structure:** {template['structure']}")
                    st.markdown(f"**Prompt:** {template['prompt'][:200]}..." if len(template['prompt']) > 200 else template['prompt'])
                    if template.get('example'):
                        st.markdown(f"**Example:**\n{template['example']}")
                    st.markdown(f"**Created:** {template.get('created_at', 'N/A')[:10]}")
                    st.markdown(f"**Updated:** {template.get('updated_at', 'N/A')[:10]}")
            
            with col2:
                if st.button(f"✏️ Edit", key=f"edit_{template['id']}", use_container_width=True):
                    st.session_state.selected_template = template
                    st.session_state.show_edit_form = True
                    st.session_state.show_create_form = False
                    st.session_state.show_versions = False
                    st.rerun()
                
                if st.button(f"📜 Versions", key=f"versions_{template['id']}", use_container_width=True):
                    st.session_state.selected_template = template
                    st.session_state.show_versions = True
                    st.session_state.show_edit_form = False
                    st.session_state.show_create_form = False
                    st.rerun()
            
            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_{template['id']}", use_container_width=True, type="secondary"):
                    # Confirmation dialog using session state
                    if st.session_state.get(f"confirm_delete_{template['id']}", False):
                        asyncio.run(delete_template(template['id'], template['name']))
                    else:
                        st.session_state[f"confirm_delete_{template['id']}"] = True
                        st.warning(f"⚠️ Click again to confirm deletion of '{template['name']}'")
                        st.rerun()
            
            st.divider()

st.markdown("---")
st.caption("💡 Tip: Templates help you maintain consistent branding and messaging across your LinkedIn posts.")
