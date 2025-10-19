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
    structure TEXT NOT NULL, -- e.g., 'Hook -> Story -> Lesson -> CTA'
    prompt TEXT NOT NULL, -- The base prompt for the LLM
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);

-- Insert sample templates
INSERT INTO templates (name, category, structure, prompt) VALUES
('Problem-Solution-Results', 'Case Study', 'Hook → Problem → Solution → Results → CTA', 
 'Create a LinkedIn case study post following this structure: Start with a compelling hook, describe the problem faced, explain the solution implemented, showcase the results achieved, and end with a call-to-action.'),

('Before-After', 'Case Study', 'Hook → Before State → Action Taken → After State → Lesson',
 'Create a LinkedIn before-after case study: Begin with an engaging hook, describe the initial state, explain what actions were taken, show the transformed state, and share the key lesson learned.'),

('Progress Update', 'Build in Public', 'Hook → What I Built → Challenges → Learnings → Next Steps',
 'Create a build-in-public progress update: Start with an attention-grabbing hook, describe what was built, discuss challenges faced, share key learnings, and outline next steps.'),

('Milestone Celebration', 'Build in Public', 'Hook → Achievement → Journey → Gratitude → Future Goals',
 'Create a milestone celebration post: Open with an exciting hook about the achievement, briefly describe the journey, express gratitude to supporters, and share future goals.'),

('Career Journey', 'Personal Story', 'Hook → Starting Point → Turning Point → Growth → Lesson',
 'Create a career journey post: Start with a relatable hook, describe the starting point, highlight the turning point, show personal growth, and share the lesson learned.'),

('Lesson Learned', 'Personal Story', 'Hook → Experience → Mistake → Insight → Application',
 'Create a lesson-learned post: Begin with a thought-provoking hook, describe the experience, acknowledge the mistake made, share the insight gained, and explain how to apply it.');
