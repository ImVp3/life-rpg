import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="helpme")
    async def helpme(self, ctx):
        embed = discord.Embed(title="📚 Danh sách lệnh Life RPG Bot", color=0x00acee)
        embed.set_footer(text="Sử dụng tiền tố `!` trước mỗi lệnh. Dùng !helpme bất cứ lúc nào để xem lại hướng dẫn.")

        embed.add_field(name="👤 Nhân vật", value=
            "`!register` - Tạo nhân vật\n"
            "`!profile` - Xem hồ sơ cá nhân\n"
            "`!delete_profile` - Xóa profile (cần xác nhận)\n"
            "`!level_status` - Xem cấp độ và tiến trình EXP\n"
            "`!level_list` - Xem EXP cần thiết từ cấp 1–10\n"
            "`!toggle_shared_habit` - Bật/tắt thói quen chung (shared habits)", inline=False)

        embed.add_field(name="🎯 Nhiệm vụ", value=
            "`!quest_list` - Danh sách nhiệm vụ\n"
            "`!quest_claim <id>` - Nhận thưởng nhiệm vụ\n"
            "`!quest_add` - Mở form để tạo nhiệm vụ mới (admin)", inline=False)

        embed.add_field(name="🧠 Thói quen", value=
            "`!habit_add` - Mở form để tạo thói quen mới\n"
            "`!habit_list` - Danh sách thói quen (cá nhân + shared)\n"
            "`!habit_all` - Xem toàn bộ thói quen với đầy đủ thông tin\n"
            "`!habit_done <id>` - Đánh dấu hoàn thành thói quen\n"
            "`!habit_toggle <id>` - Bật/tắt thói quen\n"
            "`!shared_habits_info` - Xem danh sách shared habits có sẵn", inline=False)

        embed.add_field(name="🔔 Nhắc nhở", value=
            "`!reminder` - Xem cài đặt nhắc nhở hiện tại\n"
            "`!reminder <mode>` - Cài đặt chế độ nhắc nhở\n"
            "• OFF: Tắt nhắc nhở\n"
            "• AFTER_WORK: Nhắc nhở từ 18h-23h (mặc định)\n"
            "• ALL: Nhắc nhở từ 6h-23h\n"
            "• CUSTOM: Nhắc nhở theo giờ tùy chỉnh\n"
            "`!reminder_test` - Test gửi nhắc nhở ngay lập tức", inline=False)

        embed.add_field(name="⏰ Scheduler & Hệ thống", value=
            "`!schedule_status` - Xem các job định kỳ đang chạy\n"
            "`!helpme` - Hiển thị danh sách lệnh\n"
            "Bạn có thể hỏi agent về các lệnh, tính năng, trạng thái hệ thống bằng ngôn ngữ tự nhiên.", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
