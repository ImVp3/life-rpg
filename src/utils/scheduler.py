from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import (
    get_all_quests, get_user_quests, claim_quest,
    get_user_habits, reward_stat_from_habit
)
import aiosqlite
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../database/liferpg.db")

scheduler = AsyncIOScheduler()

# 💥 Reset nhiệm vụ mỗi ngày
async def reset_daily_quests():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE user_quests
            SET completed = 0
            WHERE quest_id IN (
                SELECT id FROM (
                    SELECT json_extract(value, '$.id') AS id
                    FROM json_each(readfile('data/quests.json'))
                    WHERE json_extract(value, '$.type') = 'daily'
                )
            )
        """)
        await db.commit()
    print("[⏰] Reset nhiệm vụ daily xong")

# 🔁 Reset nhiệm vụ hàng tuần
async def reset_weekly_quests():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE user_quests
            SET completed = 0
            WHERE quest_id IN (
                SELECT id FROM (
                    SELECT json_extract(value, '$.id') AS id
                    FROM json_each(readfile('data/quests.json'))
                    WHERE json_extract(value, '$.type') = 'weekly'
                )
            )
        """)
        await db.commit()
    print("[⏰] Reset nhiệm vụ weekly xong")

# ❌ Reset streak nếu người dùng bỏ 1 ngày
async def reset_habit_streaks():
    today = date.today()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, habit_id, last_done FROM user_habits")
        rows = await cursor.fetchall()

        for user_id, habit_id, last_done in rows:
            if not last_done:
                continue
            last_date = date.fromisoformat(last_done)
            if (today - last_date).days > 1:
                await db.execute("""
                    UPDATE user_habits
                    SET streak = 0
                    WHERE user_id = ? AND habit_id = ?
                """, (user_id, habit_id))

        await db.commit()
    print("[⏰] Reset streak các thói quen bị bỏ")

# 😵 Tự động trừ điểm nếu thói quen không hoàn thành
async def penalize_missed_habits():
    today = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT uh.user_id, uh.habit_id, uh.stat_gain, uh.last_done, uh.enabled
            FROM user_habits uh
        """)
        rows = await cursor.fetchall()

        for user_id, habit_id, stat_gain, last_done, enabled in rows:
            if last_done != today and stat_gain.upper() == "INT" and enabled:
                await db.execute("""
                    UPDATE users SET int_stat = MAX(int_stat - 1, 0), hp = MAX(hp - 5, 0)
                    WHERE user_id = ?
                """, (user_id,))

        await db.commit()
    print("[⏰] Trừ điểm vì bỏ thói quen")

# 🎮 Khởi động toàn bộ job
def start_scheduler():
    scheduler.add_job(reset_daily_quests, "cron", hour=5)
    scheduler.add_job(reset_weekly_quests, "cron", day_of_week="mon", hour=5)
    scheduler.add_job(reset_habit_streaks, "cron", hour=4)
    scheduler.add_job(penalize_missed_habits, "cron", hour=23, minute=59)

    scheduler.start()
def list_scheduled_jobs():
    jobs = scheduler.get_jobs()
    return [
        {
            "id": job.id,
            "name": job.func.__name__,
            "next_run": str(job.next_run_time),
            "trigger": str(job.trigger)
        }
        for job in jobs
    ]
