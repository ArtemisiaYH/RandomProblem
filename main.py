import discord
from discord.ext import commands
import random
import aiohttp
from dotenv import load_dotenv
import os
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SERVER = os.getenv("SERVER_ID")
PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX,intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension("cogs.problem") # /problem
    await bot.load_extension("cogs.user") # /user
    await bot.tree.sync()
    guild = discord.Object(id=SERVER)
    await bot.tree.sync(guild=guild)
    print(f'Logged in as {bot.user.name}')
    print(f'登録済みコマンド: {[c.name for c in bot.tree.get_commands()]}')

bot.run(TOKEN)