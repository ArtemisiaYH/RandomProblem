import discord
from discord.ext import commands
import random
import aiohttp
from dotenv import load_dotenv
import os
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension("cogs.problem")
    print(f'Logged in as {bot.user.name}')

bot.run(TOKEN)