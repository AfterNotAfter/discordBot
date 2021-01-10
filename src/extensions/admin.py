import os
from datetime import datetime

import logging
import psutil
import discord
import config
from discord.ext import commands

from interface import is_confirmed


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author) or ctx.author.id in config.moderator_ids

    @commands.command(name="reload", brief="Hot-load specific modules.")
    async def reload(self, ctx, path):
        self.bot.reload_extension(f"extensions.{path}")
        await ctx.send(f"Successfully reloaded `{path}`!")

    @commands.command(name="uptime", brief="Check the server uptime and the bot uptime.")
    async def uptime(self, ctx):
        now = datetime.now()
        server_uptime = now - datetime.fromtimestamp(psutil.boot_time())
        python_uptime = now - datetime.fromtimestamp(
            psutil.Process(os.getpid()).create_time()
        )

        await ctx.send(
            f"**Server Uptime** {server_uptime}\n" + f"**Bot Uptime** {python_uptime}"
        )

    @commands.command(name="shutdown", brief="Shutdown the bot.")
    async def shutdown(self, ctx):
        prompt = await ctx.send("Are you really want to shutdown this bot?")
        if await is_confirmed(ctx, prompt):
            await ctx.send("OK, bye!")
            await ctx.bot.logout()

    @commands.command(brief="Shutdown the bot.")
    async def fix(self, ctx, msg_channel: discord.TextChannel, emoji_msg: int, role: discord.Role):
        msg = await msg_channel.fetch_message(emoji_msg)
        reaction = msg.reactions
        self.bot.logger.info(f"{msg_channel}: {msg}: {reaction}")
        await ctx.send(f"{msg_channel}: {msg.author}: {reaction}")
        members = []
        successCount = 0
        await ctx.send(f"반응한 유저 불러오는중....")
        async for user in reaction[0].users():
            member=await ctx.guild.fetch_member(user.id)
            members.append(member)
        await ctx.send(f"{ctx.author.mention} {len(members)}명에게 {role.name} 역할을 지급중..")
        self.bot.logger.info(members)
        
        for member in members:
            try:
                await member.add_roles(role, reason="이벤트봇 오류로 인한 미지급 해결")
                self.bot.logger.info(f"{member} 에게 {role.name} 지급성공")
                successCount +=1
            except Exception as e:
                self.bot.logger.info(f"오류: {member} 에게 {role.name} 지급중 오류 발생!\n{e}")
        await ctx.send(f"{ctx.author.mention} {len(members)}명중 {successCount}명에게 성공적으로 {role.name} 역할 지급 성공")
        

def setup(bot):
    bot.add_cog(Admin(bot))
