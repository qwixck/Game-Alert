import discord
from discord.ext import commands, tasks

import aiohttp
import json
import datetime

class EpicGames(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.epicGames.start()

    @tasks.loop(minutes=1)
    async def epicGames(self):
        await self.bot.wait_until_ready()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions") as request:
                if not request.ok:
                    print(f"Something wrong with Epic Games API! Code: {request.status}")
                epicGames = await request.json()
        await session.close()
        list = []
        with open("assets/data/games.json", "r") as f:
            games = json.load(f)
        for i in epicGames["data"]["Catalog"]["searchStore"]["elements"]:
            if i["price"]["totalPrice"]["discountPrice"] == 0 and len(i["price"]["lineOffers"][0]["appliedRules"]) != 0 and datetime.datetime.fromisoformat(str(i["price"]["lineOffers"][0]["appliedRules"][0]["endDate"]).replace("Z", "")) >= datetime.datetime.now() and i["title"] not in games:
                embed = discord.Embed(title=i["title"], description=i["description"], color=discord.Color.blurple())
                embed.set_image(url=i["keyImages"][0]["url"])
                embed.set_footer(text="Epic Games")
                list.append(embed)
                games.append(i["title"])
        with open("assets/data/games.json", "w") as f:
            json.dump(games, f, indent=2)
        with open("assets/data/channels.json", "r") as f:
            channels = json.load(f)
        for channel in channels:
            try:
                _channel = await self.bot.fetch_channel(channels[str(channel)]["channel"])
                await _channel.send(embeds=list)
            except discord.errors.HTTPException:
                pass
            except Exception as e:
                print(f"Unknown error: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(EpicGames(bot))