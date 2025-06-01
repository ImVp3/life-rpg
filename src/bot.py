import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database.db import init_db
from utils.scheduler import start_scheduler
from langchain_google_genai import ChatGoogleGenerativeAI
from agent.agent import RPGChatbotAgent
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True 


chat_fn = RPGChatbotAgent().chat

class LifeRPGBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.user")
        await self.load_extension("cogs.quest")
        await self.load_extension("cogs.habit")
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.level")
        await self.load_extension("cogs.help")

    async def on_ready(self):
        await init_db()
        start_scheduler()
        print(f"{self.user} đã sẵn sàng!")
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith("!"):
            await bot.process_commands(message)
            return
        response = await chat_fn(f"{message.author.name} (ID:{message.author.id}): {message.content}")
        await message.channel.send(response)


bot = LifeRPGBot()
bot.run(TOKEN)
