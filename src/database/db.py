import json
import os
import aiosqlite
from datetime import datetime, date, timedelta
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
        row = await cursor.fetchone()
        if not row:
            return None
        # Lấy tên cột từ cursor.description
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))

async def add_user(user_id, username):
    async with aiosqlite.connect(DB_PATH) as db:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.execute("""
            INSERT INTO users (user_id, username, level, exp, hp, int_stat, shared_habit, reminder_mode, reminder_custom_hours, created_at)
            VALUES (?, ?, 1, 0, 100, 0, 0, 'AFTER_WORK', '[]', ?)
        """, (user_id, username, current_time))
        await db.commit()

async def delete_user(user_id):
    """Xóa user và tất cả dữ liệu liên quan"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Xóa user habits
        await db.execute("DELETE FROM user_habits WHERE user_id = ?", (user_id,))
        
        # Xóa user quests
        await db.execute("DELETE FROM user_quests WHERE user_id = ?", (user_id,))
        
        # Xóa habit logs
        await db.execute("DELETE FROM habit_logs WHERE user_id = ?", (user_id,))
        
        # Xóa user
        await db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        await db.commit()

async def get_all_quests(*args, **kwargs):
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

async def reward_user(user_id, exp):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET exp = exp + ? WHERE user_id = ?",
            (exp, user_id),
        )
        await db.commit()

async def add_habit(user_id, habit_id, name, stat_gain, base_exp, base_int=0, base_hp=0, is_shared=False):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO user_habits (user_id, habit_id, name, stat_gain, base_exp, base_int, base_hp, is_shared, enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (user_id, habit_id, name, stat_gain, base_exp, base_int, base_hp, is_shared))
        await db.commit()

async def get_user_habits(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT habit_id, name, stat_gain, base_exp, streak, last_done FROM user_habits WHERE user_id = ?", (user_id,))
        return await cursor.fetchall()

async def mark_habit_done(user_id, habit_id):
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        # check streak and enabled status
        cursor = await db.execute("SELECT streak, last_done, enabled FROM user_habits WHERE user_id = ? AND habit_id = ?", (user_id, habit_id))
        row = await cursor.fetchone()
        if not row:
            return None

        old_streak, last_done, enabled = row
        
        if not enabled:
            return None  # Habit is disabled

        new_streak = old_streak + 1 if last_done == (date.today() - timedelta(days=1)).isoformat() else 1

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

async def reward_stat_from_habit(user_id, stat_gain, exp, base_int=0, base_hp=0):
    async with aiosqlite.connect(DB_PATH) as db:
        # Thưởng EXP
        await db.execute("UPDATE users SET exp = exp + ? WHERE user_id = ?", (exp, user_id))
        
        # Thưởng INT và HP dựa trên stat_gain
        if stat_gain.upper() == "INT":
            await db.execute("UPDATE users SET int_stat = int_stat + ? WHERE user_id = ?", (base_int, user_id))
        elif stat_gain.upper() == "HP":
            await db.execute("UPDATE users SET hp = hp + ? WHERE user_id = ?", (base_hp, user_id))
        
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
                SET level = ?, exp = ?, hp = hp + ?
                WHERE user_id = ?
            """, (level, exp, leveled_up * 10, user_id))
            await db.commit()
        return {
            "levels_up": leveled_up,
            "new_level": level,
            "hp_gain": leveled_up * 10
        } if leveled_up > 0 else None

# Shared habits functions
async def get_all_shared_habits(*args, **kwargs):
    with open(os.path.join(BASE_DIR, "../data/shared_habits.json"), "r", encoding="utf-8") as f:
        return json.load(f)

async def toggle_shared_habit_flag(user_id, enabled):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET shared_habit = ? WHERE user_id = ?
        """, (enabled, user_id))
        await db.commit()

async def toggle_shared_habit_flag_smart(user_id):
    """Toggle shared habit flag thông minh - tự động xác định trạng thái hiện tại và đổi ngược lại"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Lấy trạng thái hiện tại
        cursor = await db.execute("SELECT shared_habit FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        
        if not row:
            return None  # User không tồn tại
        
        current_status = row[0]
        new_status = 0 if current_status else 1
        
        await db.execute("""
            UPDATE users SET shared_habit = ? WHERE user_id = ?
        """, (new_status, user_id))
        await db.commit()
        
        return new_status

async def enable_shared_habit_flag(user_id):
    """Bật shared habit flag"""
    return await toggle_shared_habit_flag(user_id, 1)

async def disable_shared_habit_flag(user_id):
    """Tắt shared habit flag"""
    return await toggle_shared_habit_flag(user_id, 0)

async def add_shared_habits_to_user(user_id):
    """Thêm tất cả shared habits vào user khi bật flag"""
    shared_habits = await get_all_shared_habits()
    async with aiosqlite.connect(DB_PATH) as db:
        for habit in shared_habits:
            # Kiểm tra xem habit đã tồn tại chưa
            cursor = await db.execute("""
                SELECT id FROM user_habits 
                WHERE user_id = ? AND habit_id = ? AND is_shared = 1
            """, (user_id, habit["habit_id"]))
            
            if not await cursor.fetchone():
                await db.execute("""
                    INSERT INTO user_habits (user_id, habit_id, name, stat_gain, base_exp, base_int, base_hp, is_shared, enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, 1)
                """, (user_id, habit["habit_id"], habit["name"], habit["stat_gain"], 
                      habit["base_exp"], habit["base_int"], habit["base_hp"]))
        
        await db.commit()

async def disable_shared_habits_for_user(user_id):
    """Disable tất cả shared habits của user khi tắt flag"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE user_habits SET enabled = 0 
            WHERE user_id = ? AND is_shared = 1
        """, (user_id,))
        await db.commit()

async def enable_shared_habits_for_user(user_id):
    """Enable tất cả shared habits của user khi bật flag"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE user_habits SET enabled = 1 
            WHERE user_id = ? AND is_shared = 1
        """, (user_id,))
        await db.commit()

async def get_user_habits_with_status(user_id):
    """Lấy danh sách habits với trạng thái enabled/disabled"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT habit_id, name, stat_gain, base_exp, base_int, base_hp, streak, last_done, is_shared, enabled 
            FROM user_habits WHERE user_id = ?
        """, (user_id,))
        return await cursor.fetchall()

async def toggle_habit_enabled(user_id, habit_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT enabled FROM user_habits WHERE user_id = ? AND habit_id = ?", (user_id, habit_id))
        row = await cursor.fetchone()
        if not row:
            return None
        
        current_status = row[0]
        new_status = 0 if current_status else 1
        
        await db.execute("UPDATE user_habits SET enabled = ? WHERE user_id = ? AND habit_id = ?", (new_status, user_id, habit_id))
        await db.commit()
        return new_status

# Reminder functions
async def get_user_reminder_mode(user_id):
    """Lấy chế độ nhắc nhở của user"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT reminder_mode, reminder_custom_hours FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if not row:
            return None
        return {
            'mode': row[0],
            'custom_hours': json.loads(row[1]) if row[1] else []
        }

async def set_user_reminder_mode(user_id, mode, custom_hours=None):
    """Cài đặt chế độ nhắc nhở cho user"""
    async with aiosqlite.connect(DB_PATH) as db:
        if custom_hours is None:
            custom_hours = []
        
        await db.execute("""
            UPDATE users 
            SET reminder_mode = ?, reminder_custom_hours = ? 
            WHERE user_id = ?
        """, (mode, json.dumps(custom_hours), user_id))
        await db.commit()

async def get_users_with_reminders():
    """Lấy tất cả users có bật nhắc nhở (không phải OFF)"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT user_id, username, reminder_mode, reminder_custom_hours 
            FROM users 
            WHERE reminder_mode != 'OFF'
        """)
        rows = await cursor.fetchall()
        return [
            {
                'user_id': row[0],
                'username': row[1],
                'mode': row[2],
                'custom_hours': json.loads(row[3]) if row[3] else []
            }
            for row in rows
        ]

async def get_incomplete_habits_for_user(user_id):
    """Lấy danh sách thói quen chưa hoàn thành hôm nay của user"""
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT habit_id, name, stat_gain, base_exp, base_int, base_hp, is_shared
            FROM user_habits 
            WHERE user_id = ? AND enabled = 1 AND (last_done != ? OR last_done IS NULL)
        """, (user_id, today))
        return await cursor.fetchall()

