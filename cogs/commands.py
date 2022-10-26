import discord
from discord.ext import commands

import json
import aiohttp
from bs4 import BeautifulSoup

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'

    @discord.slash_command(description="Set channel where you want to free games be announced")
    async def set_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        with open("assets/data/channels.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)]["channel"] = channel.id

        with open("assets/data/channels.json", "w") as f:
            json.dump(data, f, indent=2)

        await ctx.respond(f"Successfully changed announment channel to {channel.mention}")

    @discord.slash_command(description="Get current free games")
    async def games(self, ctx: discord.ApplicationContext):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions") as request:
                if not request.ok:
                    return print(f"Something wrong with Epic Games API! Code: {request.status}")
                epicGames = await request.json()
            async with session.get("https://store.steampowered.com/search/?maxprice=free&specials=1", headers={'user-agent': self.UA }) as request:
                if not request.ok:
                    return print(f"Something wrong with Steam store! Code: {request.status}")
                sp = BeautifulSoup(await request.text(), "html.parser")
        await session.close()
        list = []
        for i in sp.find(id="search_resultsRows").find_all("a"):
            embed = discord.Embed(title=i.find("div", {"class": "responsive_search_name_combined"}).span.text, url=i["href"], color=discord.Color.blurple())
            embed.set_thumbnail(url=i.find("div", {"class": "col search_capsule"}).img["src"])
            embed.set_footer(text="Steam")
            list.append(embed)
        for i in epicGames["data"]["Catalog"]["searchStore"]["elements"]:
            if i["price"]["totalPrice"]["discountPrice"] == 0:
                embed = discord.Embed(title=i["title"], description=i["description"], color=discord.Color.blurple())
                embed.set_image(url=i["keyImages"][1]["url"])
                embed.set_footer(text="Epic Games")
                list.append(embed)
        await ctx.respond(embeds=list, ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))