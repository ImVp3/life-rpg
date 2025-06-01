import discord
from discord.ext import commands, tasks
import datetime
import asyncio

intents = discord.Intents.default()
intents.message_content = True  # Quan trọng để bot đọc nội dung tin nhắn

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập với tên: {bot.user}')
    daily_message.start()  # Bắt đầu task gửi tin nhắn định kỳ

@bot.command()
async def hello(ctx):
    await ctx.send(f'Chào {ctx.author.name}! 👋')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Không phản hồi chính mình

    if "xin chào" in message.content.lower():
        await message.channel.send("Chào bạn! Tôi là bot nè 🤖")

    await bot.process_commands(message)

@tasks.loop(seconds=10)
async def daily_message():
    now = datetime.datetime.now()
    if now.hour == 18 and now.minute == 8:  # 18:06 chiều (thay đổi tùy ý)
        channel = bot.get_channel(1207731224701837323)
        if channel:
            await channel.send("Xin chào, test thử chức năng thôi")
        else:
            print("Không tìm thấy kênh có ID 1207731224701837323")

@daily_message.before_loop
async def before():
    await asyncio.sleep(1)  # Đợi 1 giây để bot khởi động xong rồi mới chạy loop

bot.run("MTM3Nzk0NjY2NDIwNzI1NzY4MQ.GjiG9C.QOjtfLSRojtyhGtoBS9o_ryAN-zNyutKny7_BI")  # Thay bằng token bot của bạn
