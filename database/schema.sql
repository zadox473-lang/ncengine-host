-- ==========================
-- NC ENGINE HOST DATABASE
-- ==========================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,

    user_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,

    display_name TEXT DEFAULT 'User',
    owner_id BIGINT,

    hosted_count INTEGER DEFAULT 0,

    is_banned BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS bots (

    id SERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,

    bot_id BIGINT NOT NULL,
    bot_username TEXT,
    bot_name TEXT,

    bot_token TEXT UNIQUE NOT NULL,

    process_name TEXT,

    status TEXT DEFAULT 'running',

    hosted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
    REFERENCES users(user_id)
    ON DELETE CASCADE

);



CREATE TABLE IF NOT EXISTS tickets (

    id SERIAL PRIMARY KEY,

    ticket_id TEXT UNIQUE,

    user_id BIGINT NOT NULL,

    status TEXT DEFAULT 'open',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE IF NOT EXISTS settings (

    id SERIAL PRIMARY KEY,

    setting_key TEXT UNIQUE,

    setting_value TEXT

);



CREATE TABLE IF NOT EXISTS logs (

    id SERIAL PRIMARY KEY,

    user_id BIGINT,

    action TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE INDEX IF NOT EXISTS idx_users_userid
ON users(user_id);



CREATE INDEX IF NOT EXISTS idx_bots_userid
ON bots(user_id);



CREATE INDEX IF NOT EXISTS idx_bots_status
ON bots(status);



CREATE INDEX IF NOT EXISTS idx_ticket_user
ON tickets(user_id);
