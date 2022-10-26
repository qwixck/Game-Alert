import discord
from discord.ext import commands

import json

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(description="Set channel where you want to free games be announced")
    async def set_channel(ctx: discord.ApplicationContext, channel: discord.TextChannel):
        with open("assets/data/channels.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)]["channel"] = channel.id

        with open("assets/data/channels.json", "w") as f:
            json.dump(data, f, indent=2)

        await ctx.respond(f"Successfully changed announment channel to {channel.mention}")

def setup(bot: commands.Bot):
    bot.add_cog(Commands(bot))