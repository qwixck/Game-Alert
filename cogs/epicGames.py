import discord
from discord.ext import commands, tasks

import aiohttp
import json

class EpicGames(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.epicGames.start()

    @tasks.loop(minutes=1)
    async def epicGames(self):
        await self.bot.wait_until_ready()
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
                embed.set_footer(text="Epic Games")
                list.append(embed)
                games.append(i["title"])
        with open("assets/data/games.json", "w") as f:
            json.dump(games, f, indent=2)
        with open("assets/data/channels.json", "r") as f:
            channels = json.load(f)
        for channel in channels:
            _channel = await self.bot.fetch_channel(channels[str(channel)]["channel"])
            await _channel.send(embeds=list)

def setup(bot: commands.Bot):
    bot.add_cog(EpicGames(bot))