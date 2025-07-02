CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    hp INTEGER DEFAULT 100,
    int_stat INTEGER DEFAULT 0,
    shared_habit BOOLEAN DEFAULT 0,
    reminder_mode TEXT DEFAULT 'AFTER_WORK',
    reminder_custom_hours TEXT DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_quests (
    user_id INTEGER,
    quest_id TEXT,
    completed BOOLEAN DEFAULT 0,
    PRIMARY KEY (user_id, quest_id)
);

CREATE TABLE IF NOT EXISTS user_habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    habit_id TEXT,
    name TEXT,
    stat_gain TEXT,       -- INT / HP / BOTH
    base_exp INTEGER,
    base_int INTEGER DEFAULT 0,
    base_hp INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    last_done DATE,
    is_shared BOOLEAN DEFAULT 0,
    enabled BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS shared_habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id TEXT UNIQUE,
    name TEXT,
    stat_gain TEXT,       -- INT / HP / BOTH
    base_exp INTEGER,
    base_int INTEGER DEFAULT 0,
    base_hp INTEGER DEFAULT 0,
    description TEXT
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    habit_id TEXT,
    date TEXT
);
