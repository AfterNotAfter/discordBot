import discord
from discord.ext import commands
import traceback
import datetime
import asyncio
import sys
import config
import importlib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
class ModeratorCog(commands.Cog):
    def __init__(self, bot):
        importlib.reload(config)
        self.bot = bot
        #FireBase
        try:
            app = firebase_admin.get_app()
        except ValueError as e:
            cred = credentials.Certificate('./cert/firebasecert.json')
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
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


    @commands.command(name="가입링크")
    async def user_auth_link(self, ctx, member: discord.Member):
        timestamp = datetime.datetime.utcnow()
        KST = datetime.timedelta(hours=9)
        secret_embed = discord.Embed(
            color=0x7be53b,
            title=f"{member}님의 고유 가입 링크",
            description=f"[링크](https://{config.site_url}/login?discordId={member.id}&mode=register)",
            timestamp=timestamp
        )
        try:
            await member.send(embed=secret_embed)
            await ctx.send("해당 유저의 개인 DM 으로 가입 링크를 전송하였습니다!")
        except:
            await ctx.send(f'이 유저는 개인DM을 막아두어서 유저 가입 고유 링크를 보내지 못하였습니다.\n {member.mention}님은 DM을 열어주시고, 관리자 분들은 `a.인증링크 @유저멘션` 명령어를 통해 다시 DM 전송을 시도해 주세요')


def setup(bot):
    bot.add_cog(ModeratorCog(bot))
