"""Post generation service using Pydantic AI."""

from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

try:
    from pydantic_ai import Agent
    from pydantic_ai.models.openai import OpenAIModel
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False

from app.core.config import settings


class PostContext(BaseModel):
    """Context for post generation."""
    
    post_type: str = Field(..., description="Type of LinkedIn post")
    message: str = Field(..., description="Main message or topic")
    tone: str = Field(..., description="Desired tone of the post")
    reference_text: Optional[str] = Field(None, description="Reference material")


class GeneratedPost(BaseModel):
    """Structure for generated LinkedIn post."""
    
    content: str = Field(..., description="The generated post content")
    hook: str = Field(..., description="Attention-grabbing opening")
    body: str = Field(..., description="Main content/story")
    lesson: str = Field(..., description="Key takeaway or insight")
    cta: str = Field(..., description="Call to action")


class PostGeneratorService:
    """Service for generating LinkedIn posts using AI."""
    
    def __init__(self, db: Session):
        """Initialize the post generator service."""
        self.db = db
        
        # Initialize Pydantic AI agent if available
        if PYDANTIC_AI_AVAILABLE and settings.OPENAI_API_KEY:
            self.model = OpenAIModel(settings.LLM_MODEL, api_key=settings.OPENAI_API_KEY)
            self.agent = Agent(
                model=self.model,
                result_type=GeneratedPost,
                system_prompt=self._get_system_prompt()
            )
        else:
            self.agent = None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent."""
        return """You are an expert LinkedIn ghostwriter specializing in creating engaging, 
authentic, and high-performing posts. Your posts follow proven structures and are designed 
to maximize engagement, shares, and meaningful conversations.

Your task is to generate LinkedIn posts that:
1. Start with a compelling hook that grabs attention
2. Tell a story or present information in an engaging way
3. Provide clear value and actionable insights
4. End with a strong call-to-action

Structure each post using the format:
- Hook: A powerful opening line (1-2 sentences)
- Body: Main content with story/insights (3-5 paragraphs)
- Lesson: Key takeaway (1-2 sentences)
- CTA: Call to action (1 sentence)

Guidelines:
- Keep posts between 800-1500 characters
- Use short paragraphs (2-3 lines max)
- Include line breaks for readability
- Avoid excessive emojis or hashtags
- Write in first person for authenticity
- Match the requested tone and style
"""
    
    async def generate_post(
        self,
        post_type: str,
        message: str,
        tone: str,
        reference_text: Optional[str] = None
    ) -> str:
        """
        Generate a LinkedIn post using AI.
        
        Args:
            post_type: Type of post (e.g., Case Study, Motivational, How-To)
            message: Main message/topic for the post
            tone: Desired tone (e.g., Professional, Inspirational, Educational)
            reference_text: Optional reference material
            
        Returns:
            Generated post content
        """
        if not self.agent:
            # Fallback if Pydantic AI is not available
            return self._generate_fallback_post(post_type, message, tone, reference_text)
        
        # Create context
        context = PostContext(
            post_type=post_type,
            message=message,
            tone=tone,
            reference_text=reference_text
        )
        
        # Build prompt
        prompt = self._build_prompt(context)
        
        try:
            # Run AI agent
            result = await self.agent.run(prompt)
            generated = result.data
            
            # Combine structured output into final post
            post_content = self._format_post(generated)
            
            return post_content
            
        except Exception as e:
            print(f"Error generating post with AI: {e}")
            # Fallback to template-based generation
            return self._generate_fallback_post(post_type, message, tone, reference_text)
    
    async def generate_template_post(
        self,
        template,
        message: str,
        tone: str,
        reference_text: Optional[str] = None
    ) -> str:
        """
        Generate a LinkedIn post using a predefined template.
        
        Args:
            template: Template model with structure and prompt
            message: User's main message/context
            tone: Desired tone/voice
            reference_text: Optional reference material
            
        Returns:
            Generated post content following template structure
        """
        if not self.agent:
            # Fallback if Pydantic AI is not available
            return self._generate_template_fallback(template, message, tone, reference_text)
        
        # Build template-specific prompt
        prompt = self._build_template_prompt(template, message, tone, reference_text)
        
        try:
            # Run AI agent with template context
            result = await self.agent.run(prompt)
            generated = result.data
            
            # Format post with template structure
            post_content = self._format_template_post(generated, template.structure)
            
            return post_content
            
        except Exception as e:
            print(f"Error generating template post with AI: {e}")
            # Fallback to simple template
            return self._generate_template_fallback(template, message, tone, reference_text)
    
    def _build_template_prompt(self, template, message: str, tone: str, reference_text: Optional[str]) -> str:
        """Build prompt for template-based generation."""
        prompt_parts = [
            f"Generate a LinkedIn post using this template structure:",
            f"\nTemplate: {template.name} ({template.category})",
            f"Structure: {template.structure}",
            f"\nBase Instructions: {template.prompt}",
            f"\nUser's Message: {message}",
            f"Desired Tone: {tone}",
        ]
        
        if reference_text:
            prompt_parts.append(f"\nReference Material:\n{reference_text[:1000]}")
        
        prompt_parts.extend([
            "\nIMPORTANT:",
            f"- Follow the {template.structure} structure exactly",
            f"- Maintain a {tone} tone throughout",
            "- Keep the post between 800-1500 characters",
            "- Use line breaks for readability",
            "- Write in first person for authenticity"
        ])
        
        return "\n".join(prompt_parts)
    
    def _format_template_post(self, generated: GeneratedPost, structure: str) -> str:
        """Format generated content according to template structure."""
        # Similar to _format_post but respects template structure
        parts = [
            generated.hook,
            "",
            generated.body,
            "",
            f"💡 {generated.lesson}",
            "",
            generated.cta
        ]
        
        return "\n".join(parts)
    
    def _generate_template_fallback(
        self,
        template,
        message: str,
        tone: str,
        reference_text: Optional[str] = None
    ) -> str:
        """Generate fallback template post when AI is unavailable."""
        
        # Extract structure elements
        structure_parts = template.structure.split("→")
        
        # Build simple post following template
        post = f"""🔥 {message}

Following the {template.name} structure:

"""
        
        for part in structure_parts:
            post += f"{part.strip()}: Your content here based on '{message}'\n\n"
        
        post += f"""💡 Key Insight: {message}

What are your thoughts on this? Let's discuss! 👇"""
        
        return post
    
    def _build_prompt(self, context: PostContext) -> str:
        """Build the prompt for the LLM."""
        prompt_parts = [
            f"Generate a LinkedIn post with the following specifications:",
            f"- Type: {context.post_type}",
            f"- Tone: {context.tone}",
            f"- Main Message: {context.message}",
        ]
        
        if context.reference_text:
            prompt_parts.append(f"\nReference Material:\n{context.reference_text[:1000]}")
        
        prompt_parts.append("\nCreate an engaging post that follows the Hook → Body → Lesson → CTA structure.")
        
        return "\n".join(prompt_parts)
    
    def _format_post(self, generated: GeneratedPost) -> str:
        """Format the generated post into final content."""
        parts = [
            generated.hook,
            "",  # Empty line
            generated.body,
            "",  # Empty line
            f"💡 {generated.lesson}",
            "",  # Empty line
            generated.cta
        ]
        
        return "\n".join(parts)
    
    def _generate_fallback_post(
        self,
        post_type: str,
        message: str,
        tone: str,
        reference_text: Optional[str] = None
    ) -> str:
        """Generate a simple template-based post as fallback."""
        
        # Simple template-based generation
        post_templates = {
            "Case Study": f"""📊 Here's what I learned from {message}

The challenge was real. {message}

Here's what worked:
• Focused on the core problem
• Implemented a systematic approach
• Measured results continuously

The outcome? Significant improvement and valuable insights.

💡 Key takeaway: {message}

What's been your experience with similar challenges? Share below! 👇""",
            
            "Motivational": f"""✨ {message}

I've been thinking about this lately, and here's what I've realized:

{message}

It's not always easy, but it's always worth it.

💡 Remember: Every expert was once a beginner.

What motivates you to keep going? 💪""",
            
            "How-To": f"""📚 How to: {message}

Step-by-step approach:

1️⃣ Start with the basics
2️⃣ {message}
3️⃣ Practice consistently
4️⃣ Learn from feedback

💡 Pro tip: Focus on progress, not perfection.

Have you tried this approach? Let me know your thoughts! 👇""",
        }
        
        # Get template or use generic one
        template = post_templates.get(post_type, f"""{message}

Here's my perspective on this topic.

{message}

💡 Key insight: Focus on what matters most.

What do you think? Share your thoughts below! 👇""")
        
        return template
