"""SQLAlchemy database models."""

from datetime import datetime, time
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    telegram_chat_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="user")
    notification_preferences = relationship("NotificationPreferences", back_populates="user", uselist=False)
    delivery_logs = relationship("DeliveryLog", back_populates="user")


class Template(Base):
    """Template model for auto post generation."""
    
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    tone = Column(String, nullable=False, default='Professional')
    structure = Column(String, nullable=False)
    example = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="template")
    versions = relationship("TemplateVersion", back_populates="template", cascade="all, delete-orphan")


class TemplateVersion(Base):
    """Template version model for tracking template changes."""
    
    __tablename__ = "template_versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)
    structure = Column(String, nullable=False)
    tone = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=False)  # Email or user ID
    change_description = Column(Text, nullable=True)
    
    # Relationships
    template = relationship("Template", back_populates="versions")


class Post(Base):
    """Post model for storing generated content."""
    
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    generation_mode = Column(String, nullable=False)  # 'manual' or 'auto'
    status = Column(String, nullable=False, default='published')  # 'draft' or 'published'
    reference_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    template = relationship("Template", back_populates="posts")
    delivery_logs = relationship("DeliveryLog", back_populates="post")


class NotificationPreferences(Base):
    """Notification preferences model for user settings."""
    
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    receive_email_notifications = Column(Boolean, default=True)
    receive_telegram_notifications = Column(Boolean, default=True)
    daily_reminder_enabled = Column(Boolean, default=False)
    daily_reminder_time = Column(Time, default=time(9, 0, 0))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")


class DeliveryLog(Base):
    """Delivery log model for tracking notification delivery status."""
    
    __tablename__ = "delivery_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    channel = Column(String, nullable=False)  # 'email' or 'telegram'
    status = Column(String, nullable=False)  # 'delivered', 'failed', 'retried'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="delivery_logs")
    post = relationship("Post", back_populates="delivery_logs")
