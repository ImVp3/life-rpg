CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    level INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    hp INTEGER DEFAULT 100,
    gold INTEGER DEFAULT 0,
    int_stat INTEGER DEFAULT 0,
    str_stat INTEGER DEFAULT 0,
    sk_stat INTEGER DEFAULT 0,
    level_point INTEGER DEFAULT 0
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
    stat_gain TEXT,       -- INT / STR / SK
    base_exp INTEGER,
    streak INTEGER DEFAULT 0,
    last_done DATE
);

CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    habit_id TEXT,
    date TEXT
);
