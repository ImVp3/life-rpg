import discord
from discord.ext import commands
from database.db import get_user, exp_needed_for_level
import aiosqlite
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "liferpg.db")

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    percent = current / total
    filled_blocks = int(percent * length)
    empty_blocks = length - filled_blocks
    return "[" + "█" * filled_blocks + "░" * empty_blocks + f"] {int(percent * 100)}%"

class LevelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="level_status")
    async def level_status(self, ctx):
        user = await get_user(ctx.author.id)
        if not user:
            await ctx.send("Bạn chưa đăng ký.")
            return

        level = user[2]
        exp = user[3]
        needed = int(100 * (1.5 ** (level - 1)))
        bar = create_progress_bar(exp, needed)

        embed = discord.Embed(title="📈 Cấp độ & Tiến trình", color=0x9b59b6)
        embed.add_field(name="Level", value=level)
        embed.add_field(name="EXP", value=f"{exp}/{needed}\n📊 {bar}", inline=False)
        embed.add_field(name="Điểm chưa phân phối", value=user[9])
        await ctx.send(embed=embed)
    @commands.command(name="allocate")
    async def allocate(self, ctx, stat: str, amount: int):
        stat = stat.upper()
        if stat not in ["INT", "STR", "SK"]:
            await ctx.send("⚠️ Chỉ có thể phân phối vào INT, STR hoặc SK.")
            return

        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("SELECT level_point FROM users WHERE user_id = ?", (ctx.author.id,))
            row = await cursor.fetchone()
            if not row or row[0] < amount:
                await ctx.send("⚠️ Không đủ điểm để phân phối.")
                return

            await db.execute(f"""
                UPDATE users
                SET {stat.lower()}_stat = {stat.lower()}_stat + ?, level_point = level_point - ?
                WHERE user_id = ?
            """, (amount, amount, ctx.author.id))
            await db.commit()

        await ctx.send(f"✅ Đã cộng {amount} điểm vào **{stat}**.")
    @commands.command(name="level_list")
    async def level_list(self, ctx):
        embed = discord.Embed(title="📊 Bảng EXP từng cấp (Level 1–10)", color=0x3498db)
        description = ""

        for lvl in range(1, 11):
            exp = exp_needed_for_level(lvl)
            description += f"🔹 Level {lvl}: `{exp}` EXP\n"

        embed.description = description
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelCog(bot))
