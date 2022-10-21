from dotenv import load_dotenv
import os

import discord
from discord.ext import commands, tasks

import aiohttp
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

@tasks.loop(seconds=10)
async def watching():
    await bot.wait_until_ready()
    with open("assets/data/channels.json", "r") as f:
        data = json.load(f)

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(data)} channels"))

@tasks.loop(minutes=1)
async def send():
    await bot.wait_until_ready()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions") as request:
            epicGames = await request.json()
    await session.close()
    list = []
    with open("assets/data/games.json", "r") as f:
        games = json.load(f)
    for i in epicGames["data"]["Catalog"]["searchStore"]["elements"]:
        if i["price"]["totalPrice"]["discountPrice"] == 0 and not i["title"] in games:
            embed = discord.Embed(title=i["title"], description=i["description"])
            embed.set_image(url=i["keyImages"][1]["url"])
            list.append(embed)
            games.append(i["title"])
    with open("assets/data/games.json", "w") as f:
        json.dump(games, f, indent=2)
    with open("assets/data/channels.json", "r") as f:
        channels = json.load(f)
    for channel in channels:
        _channel = await bot.fetch_channel(channels[str(channel)]["channel"])
        await _channel.send(embeds=list)

watching.start()
send.start()

bot.run(os.getenv("DISCORD_TOKEN"))