import discord
from discord.ext import commands
from utils.scheduler import list_scheduled_jobs

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="schedule_status")
    async def schedule_status(self, ctx):
        jobs = list_scheduled_jobs()
        if not jobs:
            await ctx.send("⏰ Không có job nào đang chạy.")
            return

        embed = discord.Embed(title="📆 Scheduler Status", color=0xffcc00)
        for job in jobs:
            embed.add_field(
                name=f"🔧 {job['name']}",
                value=f"🕒 Chạy lúc: `{job['next_run']}`\n⏳ Trigger: `{job['trigger']}`",
                inline=False
            )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
