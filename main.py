import discord
from discord.ext import commands
import random
import aiohttp
from dotenv import load_dotenv
import os
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
sid = int(os.getenv("SERVER_ID"))
PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX,intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension("cogs.problem")
    await bot.tree.sync()
    await bot.tree.sync(guild=discord.Object(id=sid))
    print(f'Logged in as {bot.user.name}')
    print(f'登録済みコマンド: {[c.name for c in bot.tree.get_commands()]}')
async def on_interaction(interaction: discord.Interaction):
    print(f"インタラクション受信: {interaction.type} {interaction.data}")
    await bot.process_application_commands(interaction)

bot.run(TOKEN)