import discord
from discord.ext import commands, tasks
from database.db import get_user, add_user, toggle_shared_habit_flag, add_shared_habits_to_user, disable_shared_habits_for_user, enable_shared_habits_for_user, delete_user
from utils.level_fomula import get_realm_name, get_realm_description
import time

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Lưu trữ các user đang trong quá trình xác nhận xóa
        self.pending_deletions = {}
        # Bắt đầu task dọn dẹp
        self.cleanup_pending_deletions.start()

    def cog_unload(self):
        """Dừng task khi cog bị unload"""
        self.cleanup_pending_deletions.cancel()

    @tasks.loop(minutes=5)  # Chạy mỗi 5 phút
    async def cleanup_pending_deletions(self):
        """Dọn dẹp các pending deletions hết hạn"""
        current_time = time.time()
        expired_users = []
        
        for user_id, info in self.pending_deletions.items():
            if current_time - info['timestamp'] > 300:  # 5 phút
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.pending_deletions[user_id]
        
        if expired_users:
            print(f"🧹 Đã dọn dẹp {len(expired_users)} pending deletions hết hạn")

    @commands.command(name="register")
    async def register(self, ctx):
        user = await get_user(ctx.author.id)
        if user:
            await ctx.send("Bạn đã đăng ký rồi!")
        else:
            await add_user(ctx.author.id, ctx.author.name)
            await ctx.send(f"🎉 Chào mừng {ctx.author.name} đến với Life RPG!")

    @commands.command(name="profile")
    async def profile(self, ctx):
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("Bạn chưa đăng ký. Hãy dùng `/register` trước nhé.")
        else:
            # Lấy tên cảnh giới
            realm_name = get_realm_name(user['level'])
            realm_desc = get_realm_description(user['level'])
            
            embed = discord.Embed(title=f"👤 Hồ sơ Ký chủ: {user['username']}", color=0x00ff00)
            embed.add_field(name="🏆 Cảnh Giới", value=f"{realm_name} (Level {user['level']})")
            embed.add_field(name="📖 Mô Tả", value=realm_desc, inline=False)
            embed.add_field(name="🧬 Tu Vi (EXP)", value=user['exp'])
            embed.add_field(name="❤️ Sinh Lực (HP)", value=user['hp'])
            embed.add_field(name="🧠 Ngộ Tính (INT)", value=user['int_stat'])
            
            shared_status = "✅ Kích Hoạt" if user['shared_habit'] else "❌ Vô Hiệu"
            embed.add_field(name="🔗 Thói Quen Chung", value=shared_status)
            
            await ctx.send(embed=embed)

    @commands.command(name="delete_profile")
    async def delete_profile(self, ctx, confirmation_name: str = None):
        """Xóa profile của chính mình với xác nhận bảo mật"""
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("❌ Bạn chưa đăng ký. Không có gì để xóa.")
            return
        
        # Nếu chưa có xác nhận, yêu cầu nhập tên
        if confirmation_name is None:
            self.pending_deletions[ctx.author.id] = {
                'username': user['username'],
                'timestamp': ctx.message.created_at.timestamp()
            }
            
            embed = discord.Embed(
                title="⚠️ Xác nhận xóa profile",
                description=f"Bạn sắp xóa profile của **{user['username']}**\n\n"
                           f"**Dữ liệu sẽ bị xóa vĩnh viễn:**\n"
                           f"• Cảnh giới {get_realm_name(user['level'])} với {user['exp']} Tu Vi\n"
                           f"• {user['hp']} Sinh Lực và {user['int_stat']} Ngộ Tính\n"
                           f"• Tất cả thói quen và nhiệm vụ\n\n"
                           f"**Để xác nhận, hãy gõ:**\n"
                           f"`!delete_profile {user['username']}`\n\n"
                           f"⚠️ **Hệ Thống Cảnh Báo:** Đây là hành động **huỷ diệt toàn bộ lộ trình tu luyện**. Nhập chính xác tên để xác nhận. Sau xoá, không còn đường lui.",
                color=0xff0000
            )
            embed.set_footer(text="Xác nhận sẽ hết hạn sau 5 phút")
            await ctx.send(embed=embed)
            return
        
        # Kiểm tra xem user có trong danh sách pending không
        if ctx.author.id not in self.pending_deletions:
            await ctx.send("❌ Không tìm thấy yêu cầu xóa profile. Hãy dùng `!delete_profile` để bắt đầu.")
            return
        
        pending_info = self.pending_deletions[ctx.author.id]
        
        # Kiểm tra thời gian (5 phút)
        current_time = ctx.message.created_at.timestamp()
        if current_time - pending_info['timestamp'] > 300:  # 5 phút
            del self.pending_deletions[ctx.author.id]
            await ctx.send("❌ Yêu cầu xóa profile đã hết hạn. Hãy thử lại.")
            return
        
        # Kiểm tra tên xác nhận
        if confirmation_name.lower() != pending_info['username'].lower():
            await ctx.send(f"❌ Tên xác nhận không khớp. Bạn đã nhập: `{confirmation_name}`\n"
                          f"Tên cần nhập: `{pending_info['username']}`")
            return
        
        # Xác nhận thành công, thực hiện xóa
        try:
            await delete_user(ctx.author.id)
            del self.pending_deletions[ctx.author.id]
            
            embed = discord.Embed(
                title="🗑️ Profile đã được xóa",
                description=f"Profile của **{pending_info['username']}** đã được xóa vĩnh viễn.\n\n"
                           f"Tất cả dữ liệu đã bị xóa:\n"
                           f"• Thông tin nhân vật\n"
                           f"• Thói quen và nhiệm vụ\n"
                           f"• Lịch sử hoạt động\n\n"
                           f"Bạn có thể đăng ký lại bằng lệnh `!register`",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Có lỗi xảy ra khi xóa profile: {str(e)}")

    @commands.command(name="toggle_shared_habit")
    async def toggle_shared_habit(self, ctx):
        """Bật/tắt shared habits"""
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("Bạn chưa đăng ký. Hãy dùng `!register` trước.")
            return
        
        current_status = user['shared_habit']  # shared_habit flag
        new_status = not current_status
        
        await toggle_shared_habit_flag(ctx.author.id, new_status)
        
        if new_status:
            await add_shared_habits_to_user(ctx.author.id)
            await ctx.send("✅ Đã bật Shared Habits! Các thói quen chung đã được thêm vào danh sách của bạn.")
        else:
            await disable_shared_habits_for_user(ctx.author.id)
            await ctx.send("❌ Đã tắt Shared Habits! Các thói quen chung đã bị vô hiệu hóa (không bị xóa).")

async def setup(bot):
    await bot.add_cog(UserCog(bot))
