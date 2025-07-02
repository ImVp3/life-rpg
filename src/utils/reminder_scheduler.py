import os
import discord
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.db import get_users_with_reminders, get_incomplete_habits_for_user

class ReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        """Khởi động reminder scheduler"""
        # Chạy mỗi giờ để kiểm tra và gửi nhắc nhở
        self.scheduler.add_job(self.check_and_send_reminders, "interval", hours=1)
        self.scheduler.start()
        print("[⏰] Reminder scheduler đã khởi động")
    
    async def check_and_send_reminders(self):
        """Kiểm tra và gửi nhắc nhở cho tất cả users"""
        try:
            current_hour = datetime.now().hour
            users = await get_users_with_reminders()
            
            for user in users:
                should_remind = self.should_send_reminder(user, current_hour)
                if should_remind:
                    await self.send_reminder_to_user(user)
                    
        except Exception as e:
            print(f"[❌] Lỗi khi gửi nhắc nhở: {e}")
    
    def should_send_reminder(self, user, current_hour):
        """Kiểm tra xem có nên gửi nhắc nhở cho user này không"""
        mode = user['mode']
        
        if mode == 'OFF':
            return False
        elif mode == 'AFTER_WORK':
            # Nhắc nhở sau mỗi 1 giờ từ 18h
            return current_hour >= 18 and current_hour <= 23
        elif mode == 'ALL':
            # Nhắc nhở sau mỗi 1 giờ từ 6h sáng đến 23h
            return 6 <= current_hour <= 23
        elif mode == 'CUSTOM':
            # Nhắc nhở theo giờ tùy chỉnh
            return current_hour in user['custom_hours']
        
        return False
    
    async def send_reminder_to_user(self, user):
        """Gửi nhắc nhở cho một user cụ thể"""
        try:
            # Lấy channel general
            channel_id = os.getenv("GENERAL_CHANNEL")
            if not channel_id:
                print("[❌] Không tìm thấy GENERAL_CHANNEL trong .env")
                return
                
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                print(f"[❌] Không tìm thấy channel với ID {channel_id}")
                return
            
            # Lấy danh sách thói quen chưa hoàn thành
            incomplete_habits = await get_incomplete_habits_for_user(user['user_id'])
            
            if not incomplete_habits:
                return  # Không có thói quen nào cần nhắc nhở
            
            # Tạo embed nhắc nhở
            embed = discord.Embed(
                title="🔔 Nhắc Nhở Thói Quen",
                description=f"Hey <@{user['user_id']}>, đã đến giờ kiểm tra thói quen rồi!",
                color=0xff6b6b,
                timestamp=datetime.now()
            )
            
            # Phân loại thói quen
            personal_habits = []
            shared_habits = []
            
            for habit in incomplete_habits:
                habit_id, name, stat_gain, base_exp, base_int, base_hp, is_shared = habit
                
                # Tạo thông tin thưởng
                reward_info = f"Tu Vi: {base_exp}"
                if base_int > 0:
                    reward_info += f" | Ngộ Tính: +{base_int}"
                if base_hp > 0:
                    reward_info += f" | Sinh Lực: +{base_hp}"
                
                habit_info = f"• **{name}** (`{habit_id}`)\n  {reward_info}"
                
                if is_shared:
                    shared_habits.append(habit_info)
                else:
                    personal_habits.append(habit_info)
            
            # Thêm fields cho embed
            if personal_habits:
                embed.add_field(
                    name="👤 Thói Quen Cá Nhân",
                    value="\n\n".join(personal_habits),
                    inline=False
                )
            
            if shared_habits:
                embed.add_field(
                    name="🔗 Thói Quen Chung",
                    value="\n\n".join(shared_habits),
                    inline=False
                )
            
            embed.add_field(
                name="💡 Cách Hoàn Thành",
                value="Dùng lệnh `!habit_done <habit_id>` để đánh dấu hoàn thành",
                inline=False
            )
            
            embed.set_footer(text=f"Chế độ nhắc nhở: {user['mode']}")
            
            # Gửi nhắc nhở
            await channel.send(content=f"<@{user['user_id']}>", embed=embed)
            print(f"[✅] Đã gửi nhắc nhở cho {user['username']} (ID: {user['user_id']})")
            
        except Exception as e:
            print(f"[❌] Lỗi khi gửi nhắc nhở cho user {user['user_id']}: {e}")

# Global instance
reminder_scheduler = None

def init_reminder_scheduler(bot):
    """Khởi tạo reminder scheduler"""
    global reminder_scheduler
    reminder_scheduler = ReminderScheduler(bot)
    reminder_scheduler.start()
    return reminder_scheduler 