import discord
from discord.ext import commands

import traceback
import sys

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is online!")

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.errors.NotOwner):
            await ctx.respond("This command is owner only!")
        elif isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.respond(f"I'm missing the following permission(s) to execute this command: {', '.join(error.missing_permissions)}")
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.respond(f"You're missing the following permission(s) to execute this command: {', '.join(error.missing_permissions)}")
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.respond(f"Something went wrong while invoking this command")
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.respond(f"Cooldown is active. Try again in `{round(error.retry_after, 1)}` seconds")
        elif isinstance(error, commands.errors.MissingAnyRole):
            await ctx.respond(f"You are missing the following role(s): {error.missing_roles}")
        elif isinstance(error, commands.errors.NSFWChannelRequired):
            await ctx.respond("This command requires to be executed in a NSFW channel")
        else:  
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await ctx.respond("Something unexpected happened! If you believe this is not because of you, please contact the bot owner.")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.errors.NotOwner):
            await ctx.send("This command is owner only!")
        elif isinstance(error, commands.errors.BotMissingPermissions):
            await ctx.send(f"I'm missing the following permission(s) to execute this command: {', '.join(error.missing_permissions)}")
        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"You're missing the following permission(s) to execute this command: {', '.join(error.missing_permissions)}")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(f"You are missing the following argument to execute this command: `{error.param}`")
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send(f"Something went wrong while invoking this command")
        elif isinstance(error, commands.errors.CommandOnCooldown):
            await ctx.send(f"Cooldown is active. Try again in `{round(error.retry_after, 1)}` seconds")
        elif isinstance(error, commands.errors.MissingAnyRole):
            await ctx.send(f"You are missing the following role(s): {error.missing_roles}")
        elif isinstance(error, commands.errors.NSFWChannelRequired):
            await ctx.send("This command requires to be executed in a NSFW channel")
        elif isinstance(error, commands.errors.MemberNotFound):
            await ctx.send("Member wasn't found")
        else:  
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            await ctx.send("Something unexpected happened! If you believe this is not because of you, please contact the bot owner.")

def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))