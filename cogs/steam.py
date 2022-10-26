import discord
from discord.ext import commands, tasks

import aiohttp
import json
from bs4 import BeautifulSoup

class Steam(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        self.steam.start()

    @tasks.loop(minutes=1)
    async def steam(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://store.steampowered.com/search/?maxprice=free&specials=1", headers={'user-agent': self.UA }) as request:
                if not request.ok:
                    return print(f"Something wrong with Steam store! Code: {request.status}")
                sp = BeautifulSoup(await request.text(), "html.parser")
        await session.close()
        list = []
        with open("assets/data/games.json", "r") as f:
            games = json.load(f)
        for i in sp.find(id="search_resultsRows").find_all("a"):
            if not i.find("div", {"class": "responsive_search_name_combined"}).span.text in games:
                embed = discord.Embed(title=i.find("div", {"class": "responsive_search_name_combined"}).span.text, url=i["href"], color=discord.Color.blurple())
                embed.set_thumbnail(url=i.find("div", {"class": "col search_capsule"}).img["src"])
                embed.set_footer(text="Steam")
                list.append(embed)
                games.append(i.find("div", {"class": "responsive_search_name_combined"}).span.text)
        with open("assets/data/games.json", "w") as f:
            json.dump(games, f, indent=2)
        with open("assets/data/channels.json", "r") as f:
            channels = json.load(f)
        for channel in channels:
            _channel = await self.bot.fetch_channel(channels[str(channel)]["channel"])
            try:
                await _channel.send(embeds=list)
            except discord.errors.HTTPException:
                pass

def setup(bot: commands.Bot):
    bot.add_cog(Steam(bot))