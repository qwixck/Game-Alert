from dotenv import load_dotenv
import os

import discord
from discord.ext import commands, tasks

import json

load_dotenv()

bot = commands.Bot(command_prefix=commands.when_mentioned_or("g!"))

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

@bot.slash_command(description="Set channel where you want to free games be announced")
async def set_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
    with open("assets/data/channels.json", "r") as f:
        data = json.load(f)

    data[str(ctx.guild.id)] = {}
    data[str(ctx.guild.id)]["channel"] = channel.id

    with open("assets/data/channels.json", "w") as f:
        json.dump(data, f, indent=2)

    await ctx.respond(f"Successfully changed announment channel to {channel.mention}")

@tasks.loop(minutes=1)
async def watching():
    await bot.wait_until_ready()
    with open("assets/data/channels.json", "r") as f:
        data = json.load(f)

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(data)} channels"))

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

watching.start()

bot.run(os.getenv("DISCORD_TOKEN"))