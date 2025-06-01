import discord
from discord.ext import commands
from database.db import (
    get_user, add_habit, get_user_habits, mark_habit_done, reward_stat_from_habit, try_level_up
)

class HabitCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="habit_add")
    async def habit_add(self, ctx, habit_id: str, stat_gain: str, exp: int, *, name: str):
        """Thêm thói quen mới: !habit_add code_5h SK 80 Code ít nhất 5 giờ"""
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("Bạn chưa đăng ký. Dùng `!register` trước.")
            return
        await add_habit(ctx.author.id, habit_id, name, stat_gain, exp)
        await ctx.send(f"✅ Thêm thói quen **{name}** thành công!")

    @commands.command(name="habit_list")
    async def habit_list(self, ctx):
        habits = await get_user_habits(ctx.author.id)
        if not habits:
            await ctx.send("❌ Bạn chưa có thói quen nào.")
            return

        embed = discord.Embed(title="📋 Danh sách thói quen", color=0x2ecc71)
        for habit in habits:
            embed.add_field(
                name=f"{habit[1]} (`{habit[0]}`)",
                value=f"Chỉ số: {habit[2]} | EXP: {habit[3]} | Strike: {habit[4]} ngày",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="habit_done")
    async def habit_done(self, ctx, habit_id: str):
        streak = await mark_habit_done(ctx.author.id, habit_id)
        if streak is None:
            await ctx.send("⚠️ Không tìm thấy thói quen.")
            return

        habits = await get_user_habits(ctx.author.id)
        habit = next((h for h in habits if h[0] == habit_id), None)
        if not habit:
            await ctx.send("❌ Lỗi nội bộ: không tìm thấy thói quen.")
            return

        bonus_exp = habit[3] + 10 * (streak - 1)
        await reward_stat_from_habit(ctx.author.id, habit[2], bonus_exp)
        await ctx.send(f"🎉 Hoàn thành **{habit[1]}**! +{bonus_exp} EXP, +1 {habit[2]} (Strike {streak})")
        result = await try_level_up(ctx.author.id)
        if result:
            embed = discord.Embed(
                title="🎉 Bạn đã lên cấp!",
                description=f"**{ctx.author.display_name}** đã đạt cấp độ **{result['new_level']}**!",
                color=0xffd700
            )
            embed.add_field(name="🏅 Cấp độ mới", value=result["new_level"])
            embed.add_field(name="✨ Điểm nâng cấp", value=f"+{result['level_point_gain']} điểm")
            embed.add_field(name="❤️ HP hồi phục", value=f"+{result['hp_gain']} HP")
            embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)
            await ctx.send(embed=embed)
async def setup(bot):
    await bot.add_cog(HabitCog(bot))
