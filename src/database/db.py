import json
import os
import aiosqlite
import datetime
from utils.level_fomula import exp_needed_for_level

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "liferpg.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        with open("src/database/schema.sql", "r") as f:
            await db.executescript(f.read())
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()

async def add_user(user_id, username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, username)
            VALUES (?, ?)
        """, (user_id, username))
        await db.commit()
        
async def get_all_quests():
    with open(os.path.join(BASE_DIR, "../data/quests.json"), "r", encoding="utf-8") as f:
        return json.load(f)

async def get_user_quests(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT quest_id, completed FROM user_quests WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchall()

async def add_user_quests(user_id, quest_ids):
    async with aiosqlite.connect(DB_PATH) as db:
        for qid in quest_ids:
            await db.execute(
                "INSERT OR IGNORE INTO user_quests (user_id, quest_id) VALUES (?, ?)",
                (user_id, qid),
            )
        await db.commit()

async def claim_quest(user_id, quest_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE user_quests SET completed = 1 WHERE user_id = ? AND quest_id = ?",
            (user_id, quest_id),
        )
        await db.commit()

async def reward_user(user_id, exp, gold):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET exp = exp + ?, gold = gold + ? WHERE user_id = ?",
            (exp, gold, user_id),
        )
        await db.commit()
async def add_habit(user_id, habit_id, name, stat_gain, base_exp):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_habits (user_id, habit_id, name, stat_gain, base_exp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, habit_id, name, stat_gain, base_exp))
        await db.commit()

async def get_user_habits(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT habit_id, name, stat_gain, base_exp, streak, last_done FROM user_habits WHERE user_id = ?", (user_id,))
        return await cursor.fetchall()

async def mark_habit_done(user_id, habit_id):
    today = datetime.date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        # check streak
        cursor = await db.execute("SELECT streak, last_done FROM user_habits WHERE user_id = ? AND habit_id = ?", (user_id, habit_id))
        row = await cursor.fetchone()
        if not row:
            return None

        old_streak, last_done = row
        new_streak = old_streak + 1 if last_done == (datetime.date.today() - datetime.timedelta(days=1)).isoformat() else 1

        await db.execute("""
            UPDATE user_habits
            SET streak = ?, last_done = ?
            WHERE user_id = ? AND habit_id = ?
        """, (new_streak, today, user_id, habit_id))

        await db.execute("""
            INSERT INTO habit_logs (user_id, habit_id, date)
            VALUES (?, ?, ?)
        """, (user_id, habit_id, today))

        await db.commit()
        return new_streak

async def reward_stat_from_habit(user_id, stat_gain, exp):
    async with aiosqlite.connect(DB_PATH) as db:
        stat_column = {
            "INT": "int_stat",
            "STR": "str_stat",
            "SK": "sk_stat"
        }.get(stat_gain.upper(), None)

        if stat_column:
            await db.execute(f"""
                UPDATE users SET exp = exp + ?, {stat_column} = {stat_column} + 1
                WHERE user_id = ?
            """, (exp, user_id))
        else:
            await db.execute("UPDATE users SET exp = exp + ? WHERE user_id = ?", (exp, user_id))
        await db.commit()
        
async def try_level_up(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT level, exp FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return None

        level, exp = row
        leveled_up = 0

        while exp >= exp_needed_for_level(level):
            exp -= exp_needed_for_level(level)
            level += 1
            leveled_up += 1

        if leveled_up > 0:
            await db.execute("""
                UPDATE users
                SET level = ?, exp = ?, level_point = level_point + ?, hp = hp + ?
                WHERE user_id = ?
            """, (level, exp, leveled_up * 3, leveled_up * 10, user_id))
            await db.commit()
        return {
            "levels_up": leveled_up,
            "new_level": level,
            "level_point_gain": leveled_up * 3,
            "hp_gain": leveled_up * 10
        } if leveled_up > 0 else None

