import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="helpme")
    async def helpme(self, ctx):
        embed = discord.Embed(title="📚 Danh sách lệnh Life RPG Bot", color=0x00acee)
        embed.set_footer(text="Sử dụng tiền tố `!` trước mỗi lệnh.")

        embed.add_field(name="👤 Nhân vật", value=
            "`!register` - Tạo nhân vật\n"
            "`!profile` - Xem hồ sơ cá nhân\n"
            "`!level_status` - Xem cấp độ và tiến trình EXP\n"
            "`!allocate <stat> <số>` - Phân phối điểm (INT, STR, SK)\n"
            "`!level_list` - Xem EXP cần thiết từ cấp 1–10", inline=False)

        embed.add_field(name="🎯 Nhiệm vụ", value=
            "`!quest_list` - Danh sách nhiệm vụ\n"
            "`!quest_claim <id>` - Nhận thưởng nhiệm vụ", inline=False)

        embed.add_field(name="🧠 Thói quen", value=
            "`!habit_add <id> <stat> <exp> <tên>` - Thêm thói quen\n"
            "`!habit_list` - Danh sách thói quen\n"
            "`!habit_done <id>` - Đánh dấu hoàn thành", inline=False)

        embed.add_field(name="⏰ Scheduler & Hệ thống", value=
            "`!schedule_status` - Xem các job định kỳ đang chạy\n"
            "`!helpme` - Hiển thị danh sách lệnh", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
