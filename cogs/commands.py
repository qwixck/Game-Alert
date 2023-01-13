import discord
from discord.ext import commands, pages

import json
import aiohttp
from bs4 import BeautifulSoup
import datetime

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        self.steamIcon = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/512px-Steam_icon_logo.svg.png"
        self.epicGamesIcon = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Epic_Games_logo.svg/1764px-Epic_Games_logo.svg.png"

    @commands.slash_command(description="Set channel where you want to free games be announced")
    async def set_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        with open("./src/data/channels.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)]["channel"] = channel.id
        old_channel = data[str(ctx.guild.id)]["channel"]

        with open("./src/data/channels.json", "w") as f:
            json.dump(data, f, indent=2)

        embed = discord.Embed(title="Success", description=f"Successfully changed channel from {old_channel if old_channel else None} to {channel.mention}", timestamp=datetime.datetime.utcnow(), color=discord.Color.blurple())
        await ctx.respond(embed=embed)

    @commands.slash_command(description="Menu for configurating bot")
    async def menu(self, ctx: discord.ApplicationContext):
        class Select(discord.ui.Select):
            def __init__(self):
                super().__init__(placeholder="Choose option")
                self.add_option(label="Current channel", description="See the current announcement channel", emoji="📝", value="channel")
                self.add_option(label="Commands", description="See all commands that are available", emoji="📄", value="commands")
                self.add_option(label="Settings", description="Not available yet!", emoji="⚙", value="settings")

                async def callback(interaction: discord.Interaction):
                    if interaction.user != ctx.author:
                        await interaction.response.send_message("Sorry, you can't do that!", ephemeral=True)
                    else:
                        if self.values[0] == "channel":
                            with open("./src/data/channels.json", "r") as f:
                                data = json.load(f)
                            try:
                                channel = f"<#{data[str(ctx.guild.id)]['channel']}>"
                            except KeyError:
                                channel = None
                            embed = discord.Embed(title="Current announcement channel", description=f"The current channel is {channel}", timestamp=datetime.datetime.utcnow(), color=discord.Color.blurple())
                            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
                            await interaction.response.edit_message(embed=embed)
                        if self.values[0] == "commands":
                            embed = discord.Embed(title="Commands", timestamp=datetime.datetime.utcnow(), color=discord.Color.blurple())
                            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
                            embed.add_field(name="</games:0>", value="> `Get all free games that are available`")
                            embed.add_field(name="</set_channel:0>", value="> `Set channel for announcements`")
                            embed.add_field(name="</menu:0>", value="> `Menu for configurating bot`")
                            embed.add_field(name="</status:0>", value="> `Get all stores status`")
                            embed.add_field(name="</ping:0>", value="> `Shows bot's ping`")
                            await interaction.response.edit_message(embed=embed)
                        if self.values[0] == "settings":
                            embed = discord.Embed(title="Still developing", description="Not available right now...", timestamp=datetime.datetime.utcnow(), color=discord.Color.blurple())
                            await interaction.response.send_message(embed=embed, ephemeral=True)
                            
                self.callback = callback
        embed = discord.Embed(title="Menu", description="Available configurations for bot", timestamp=datetime.datetime.utcnow(), color=discord.Color.blurple())
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.add_field(name="📝 Channel", value="> `Current channel`")
        embed.add_field(name="📄 Commands", value="> `See all commands that are available`")
        embed.add_field(name="⚙ Settings", value="> `Not available yet!`")
        view = discord.ui.View(timeout=None)
        view.add_item(Select())
        await ctx.respond(embed=embed, view=view)

    @commands.slash_command(description="Get current free games")
    async def games(self, ctx: discord.ApplicationContext):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions") as request:
                if not request.ok:
                    print(f"Something wrong with Epic Games API! Code: {request.status}")
                epicGames = await request.json()
            async with session.get("https://store.steampowered.com/search/?maxprice=free&specials=1", headers={'user-agent': self.UA }) as request:
                if not request.ok:
                    print(f"Something wrong with Steam store! Code: {request.status}")
                sp = BeautifulSoup(await request.text(), "html.parser")
        await session.close()
        list = []
        try:
            for i in sp.find(id="search_resultsRows").find_all("a"):
                embed = discord.Embed(title=i.find("div", {"class": "responsive_search_name_combined"}).span.text, url=i["href"], color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
                embed.set_thumbnail(url=i.find("div", {"class": "col search_capsule"}).img["src"])
                embed.set_author(name="Steam", icon_url=self.steamIcon)
                list.append(embed)
        except AttributeError:
            pass
        for i in epicGames["data"]["Catalog"]["searchStore"]["elements"]:
            if i["promotions"]:
                if i["promotions"]["promotionalOffers"]:
                    if not i["price"]["totalPrice"]["discountPrice"]:
                        embed = discord.Embed(title=i["title"], description=i["description"], url=f"https://epicgames.com/store/product/{i['productSlug']}", color=discord.Color.blurple())
                        embed.set_image(url=i["keyImages"][0]["url"])
                        embed.set_author(name="Epic Games", icon_url=self.epicGamesIcon)
                        list.append(embed)
        # 899 because ephemeral cannot be sended with 15min timeout or greater
        await pages.Paginator(list, timeout=899, disable_on_timeout=True).respond(ctx.interaction, ephemeral=True)

    @commands.slash_command(description="Get all stores status")
    async def status(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            epicGames = await session.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions")
            steam = await session.get("https://store.steampowered.com/search/?maxprice=free&specials=1", headers={'user-agent': self.UA })
        await session.close()
        embed = discord.Embed(title="Status", color=discord.Color.blurple(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Epic Games", value=f"Status code: {epicGames.status}", inline=False)
        embed.add_field(name="Steam", value=f"Status code: {steam.status}", inline=False)
        embed.set_author(name="Click to see all codes description", url="https://developer.mozilla.org/en-US/docs/Web/HTTP/Status")
        await ctx.respond(embed=embed)

    @commands.slash_command(description="Shows bot's ping")
    async def ping(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="Pong!", description=f"⏳: {round(self.bot.latency * 1000)} ms", color=discord.Color.blurple(), timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        await ctx.respond(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))