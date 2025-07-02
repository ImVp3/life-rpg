import discord
from discord.ext import commands
from database.db import get_user, exp_needed_for_level
from utils.level_fomula import get_realm_name, get_realm_description
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

        level = user['level']
        exp = user['exp']
        needed = int(100 * (1.5 ** (level - 1)))
        bar = create_progress_bar(exp, needed)
        
        # Lấy tên cảnh giới
        realm_name = get_realm_name(level)
        realm_desc = get_realm_description(level)

        embed = discord.Embed(title="📈 Cảnh Giới & Tiến Trình Tu Luyện", color=0x9b59b6)
        embed.add_field(name="🏆 Cảnh Giới", value=f"{realm_name} (Level {level})")
        embed.add_field(name="📖 Mô Tả", value=realm_desc, inline=False)
        embed.add_field(name="🧬 Tu Vi", value=f"{exp}/{needed}\n📊 {bar}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="level_list")
    async def level_list(self, ctx):
        embed = discord.Embed(title="📊 Bảng Tu Vi từng Cảnh Giới (Level 1–10)", color=0x3498db)
        description = ""

        for lvl in range(1, 11):
            exp = exp_needed_for_level(lvl)
            realm_name = get_realm_name(lvl)
            description += f"🔹 {realm_name} (Level {lvl}): `{exp}` Tu Vi\n"

        embed.description = description
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelCog(bot))
