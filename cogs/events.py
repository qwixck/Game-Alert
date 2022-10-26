import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is online!")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        print(error)
        owner = await self.bot.fetch_user(self.bot.owner_id)
        await owner.send(f"Error!\n```\n{error}\n```")
        await ctx.respond("There's something wrong with me! Owner was already notified. Please wait for fix.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        print(error)
        owner = await self.bot.fetch_user(self.bot.owner_id)
        await owner.send(f"Error!\n```\n{error}\n```")
        await ctx.send("There's something wrong with me! Owner was already notified. Please wait for fix.")

def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))