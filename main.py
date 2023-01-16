from dotenv import load_dotenv
import os

import discord
from discord.ext import commands, tasks

import json

intents = discord.Intents.default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents, help_command=None)

@tasks.loop(minutes=1)
async def watching():
    await bot.wait_until_ready()
    with open("./src/data/channels.json", "r") as f:
        data: dict = json.load(f)

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(data)} channels"))

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

watching.start()

load_dotenv("./.env")
bot.run(os.getenv("DISCORD_TOKEN"))