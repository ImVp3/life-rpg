import discord
from discord.ext import commands
from database.db import get_user, add_user

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            embed = discord.Embed(title=f"Hồ sơ của {user[1]}", color=0x00ff00)
            embed.add_field(name="Level", value=user[2])
            embed.add_field(name="EXP", value=user[3])
            embed.add_field(name="HP", value=user[4])
            embed.add_field(name="Gold", value=user[5])
            embed.add_field(name="INT", value=user[6])
            embed.add_field(name="STR", value=user[7])
            embed.add_field(name="SK", value=user[8])
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCog(bot))
