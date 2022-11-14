import discord
from discord.ext import commands

import json
import aiohttp
from bs4 import BeautifulSoup
import datetime

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'

    @commands.slash_command(description="Set channel where you want to free games be announced")
    async def set_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        with open("assets/data/channels.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)]["channel"] = channel.id
        old_channel = data[str(ctx.guild.id)]["channel"]

        with open("assets/data/channels.json", "w") as f:
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
                        await interaction.response.send_message("Sorry, you can't do that!")
                    else:
                        if self.values[0] == "channel":
                            with open("assets/data/channels.json", "r") as f:
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
                    raise discord.errors.ApplicationCommandError()
                epicGames = await request.json()
            async with session.get("https://store.steampowered.com/search/?maxprice=free&specials=1", headers={'user-agent': self.UA }) as request:
                if not request.ok:
                    print(f"Something wrong with Steam store! Code: {request.status}")
                    raise discord.errors.ApplicationCommandError()
                sp = BeautifulSoup(await request.text(), "html.parser")
        await session.close()
        list = []
        for i in sp.find(id="search_resultsRows").find_all("a"):
            embed = discord.Embed(title=i.find("div", {"class": "responsive_search_name_combined"}).span.text, url=i["href"], color=discord.Color.blurple())
            embed.set_thumbnail(url=i.find("div", {"class": "col search_capsule"}).img["src"])
            embed.set_footer(text="Steam")
            list.append(embed)
        for i in epicGames["data"]["Catalog"]["searchStore"]["elements"]:
            if i["price"]["totalPrice"]["discountPrice"] == 0 and len(i["price"]["lineOffers"][0]["appliedRules"]) != 0 and datetime.datetime.fromisoformat(str(i["price"]["lineOffers"][0]["appliedRules"][0]["endDate"]).replace("Z", "")) >= datetime.datetime.now():
                embed = discord.Embed(title=i["title"], description=i["description"], color=discord.Color.blurple())
                embed.set_image(url=i["keyImages"][1]["url"])
                embed.set_footer(text="Epic Games")
                list.append(embed)
        await ctx.respond(embeds=list, ephemeral=True)

    @commands.slash_command(description="Get all stores status")
    async def status(self, ctx: discord.ApplicationContext):
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