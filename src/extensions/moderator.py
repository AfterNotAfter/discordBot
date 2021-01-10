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
    @commands.command(name="강제승인")
    async def force_approve(self, ctx, member: discord.Member):
        log_channel = self.bot.get_channel(config.discord_log_channel)
        verify_channel = self.bot.get_channel(config.discord_verify_channel)
        user_role = ctx.guild.get_role(config.discord_user_role)
        await member.add_roles(user_role, reason="관리자 강제 승인")
        await log_channel.send(f"관리자 {ctx.author.mention}님이 {member.mention}님을 강제승인 했습니다.")
        await verify_channel.send(f"관리자 {ctx.author.mention}님이 {member.mention}님을 강제승인 했습니다.")
        await ctx.send(f"{ctx.author.mention} 가입 승인 성공!")

def setup(bot):
    bot.add_cog(ModeratorCog(bot))
