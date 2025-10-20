-- LinkedIn Ghostwriter Database Schema
-- SQLite Database Schema for storing users, templates, and posts

-- Users Table: Stores basic user information and preferences.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    telegram_chat_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates Table: Stores predefined post templates for Auto Post Mode.
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL, -- e.g., 'Case Study', 'Build in Public'
    tone TEXT NOT NULL DEFAULT 'Professional', -- e.g., 'Professional', 'Casual', 'Inspirational'
    structure TEXT NOT NULL, -- e.g., 'Hook -> Story -> Lesson -> CTA'
    example TEXT, -- Example post using this template
    prompt TEXT NOT NULL, -- The base prompt for the LLM
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Template Versions Table: Maintains version history for template prompts and structures.
CREATE TABLE IF NOT EXISTS template_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    structure TEXT NOT NULL,
    tone TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL, -- Email or user ID of who made the change
    change_description TEXT, -- Description of what changed
    FOREIGN KEY (template_id) REFERENCES templates (id) ON DELETE CASCADE
);

-- Posts Table: Stores the history of all generated posts.
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    template_id INTEGER, -- Can be NULL if generated in Create Post Mode
    generation_mode TEXT NOT NULL, -- 'manual' or 'auto'
    status TEXT NOT NULL DEFAULT 'published', -- 'draft' or 'published'
    reference_text TEXT, -- To store extracted text from uploads
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (template_id) REFERENCES templates (id)
);

-- Notification Preferences Table: Stores user-specific notification settings.
CREATE TABLE IF NOT EXISTS notification_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    receive_email_notifications BOOLEAN DEFAULT TRUE,
    receive_telegram_notifications BOOLEAN DEFAULT TRUE,
    daily_reminder_enabled BOOLEAN DEFAULT FALSE,
    daily_reminder_time TIME DEFAULT '09:00:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Delivery Logs Table: Logs the status of every notification sent.
CREATE TABLE IF NOT EXISTS delivery_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER,
    channel TEXT NOT NULL, -- 'email' or 'telegram'
    status TEXT NOT NULL, -- 'delivered', 'failed', 'retried'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (post_id) REFERENCES posts (id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
CREATE INDEX IF NOT EXISTS idx_template_versions_template_id ON template_versions(template_id);
CREATE INDEX IF NOT EXISTS idx_template_versions_version ON template_versions(template_id, version);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user_id ON notification_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_user_id ON delivery_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_post_id ON delivery_logs(post_id);
CREATE INDEX IF NOT EXISTS idx_delivery_logs_status ON delivery_logs(status);

-- Insert sample templates
INSERT INTO templates (name, category, tone, structure, example, prompt) VALUES
('Problem-Solution-Results', 'Case Study', 'Professional', 'Hook → Problem → Solution → Results → CTA',
 'Ever faced a challenge that seemed impossible? Last quarter, our team struggled with 40% cart abandonment. We implemented a 3-step checkout flow. Result: 25% increase in conversions. Here''s what we learned...',
 'Create a LinkedIn case study post following this structure: Start with a compelling hook, describe the problem faced, explain the solution implemented, showcase the results achieved, and end with a call-to-action.'),

('Before-After', 'Case Study', 'Conversational', 'Hook → Before State → Action Taken → After State → Lesson',
 'A year ago, I was drowning in spreadsheets managing 50+ clients manually. Today? Fully automated with a custom CRM. What changed everything was...',
 'Create a LinkedIn before-after case study: Begin with an engaging hook, describe the initial state, explain what actions were taken, show the transformed state, and share the key lesson learned.'),

('Progress Update', 'Build in Public', 'Casual', 'Hook → What I Built → Challenges → Learnings → Next Steps',
 'Week 12 of building in public: Just shipped the payment integration! It took 3 failed attempts, 47 error messages, and countless coffee cups. But here''s what I learned about Stripe webhooks...',
 'Create a build-in-public progress update: Start with an attention-grabbing hook, describe what was built, discuss challenges faced, share key learnings, and outline next steps.'),

('Milestone Celebration', 'Build in Public', 'Inspirational', 'Hook → Achievement → Journey → Gratitude → Future Goals',
 '🎉 10,000 users! When I started this journey 6 months ago in my garage, I never imagined reaching this milestone. Thank you to everyone who believed in the vision. Next stop: 100K!',
 'Create a milestone celebration post: Open with an exciting hook about the achievement, briefly describe the journey, express gratitude to supporters, and share future goals.'),

('Career Journey', 'Personal Story', 'Reflective', 'Hook → Starting Point → Turning Point → Growth → Lesson',
 'From rejected 47 times to landing my dream role at Google. The turning point? Realizing failure wasn''t the opposite of success—it was part of it. Here''s my journey...',
 'Create a career journey post: Start with a relatable hook, describe the starting point, highlight the turning point, show personal growth, and share the lesson learned.'),

('Lesson Learned', 'Personal Story', 'Honest', 'Hook → Experience → Mistake → Insight → Application',
 'I once burned $10K on a product nobody wanted. Brutal lesson: Build for people, not ideas. Here''s what I wish I knew before starting...',
 'Create a lesson-learned post: Begin with a thought-provoking hook, describe the experience, acknowledge the mistake made, share the insight gained, and explain how to apply it.');
