import discord
from discord.ext import commands
import traceback
import datetime
import asyncio
import sys
import config

class ModeratorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

def setup(bot):
    bot.add_cog(ModeratorCog(bot))
