import discord
from discord.ext import commands, tasks

import aiohttp
import json
from bs4 import BeautifulSoup
import datetime

class Steam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        self.steamIcon = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/512px-Steam_icon_logo.svg.png"
        self.steam.start()

    @tasks.loop(minutes=1)
    async def steam(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://store.steampowered.com/search/?maxprice=free&specials=1", headers={'user-agent': self.UA }) as request:
                if not request.ok:
                    print(f"Something wrong with Steam store! HTTP code: {request.status}")
                sp = BeautifulSoup(await request.text(), "html.parser")
        await session.close()
        list = []
        with open("./src/data/games.json", "r") as f:
            games: dict = json.load(f)
        try:
            for i in sp.find(id="search_resultsRows").find_all("a"):
                if not i.find("div", {"class": "responsive_search_name_combined"}).span.text in games["games"]:
                    embed = discord.Embed(title=i.find("div", {"class": "responsive_search_name_combined"}).span.text, url=i["href"], color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
                    embed.set_thumbnail(url=i.find("div", {"class": "col search_capsule"}).img["src"])
                    embed.set_author(name="Steam", icon_url=self.steamIcon)
                    list.append(embed)
                    games["games"].append(i.find("div", {"class": "responsive_search_name_combined"}).span.text)
        # if no games/dlcs are available
        except AttributeError:
            pass
        with open("./src/data/games.json", "w") as f:
            json.dump(games, f, indent=2)
        with open("./src/data/channels.json", "r") as f:
            channels: dict = json.load(f)
        for channel in channels:
            try:
                _channel = self.bot.get_channel(channels[str(channel)]["channel"])
                await _channel.send(embeds=list)
            except discord.errors.HTTPException:
                pass
            except AttributeError:
                pass
            except Exception as e:
                print(f"Unknown error: {e}")

def setup(bot: commands.Bot):
    bot.add_cog(Steam(bot))