import discord
from discord.ext import commands
import traceback
import datetime
import asyncio
import sys
import config
import utils
import importlib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import Optional
class UserCog(commands.Cog):
    def __init__(self, bot):
        importlib.reload(config)
        #FireBase
        try:
            app = firebase_admin.get_app()
        except ValueError as e:
            cred = credentials.Certificate('./cert/firebasecert.json')
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
        self.bot = bot
    def cog_check(self, ctx):
        return True
    @commands.command(name="screenshot", brief="스크린샷")
    async def command_screenshot(self, ctx, twitter_id: str):
        if not twitter_id.startswith("@"):
            return await ctx.send(f"{ctx.author.mention} `a.스크린샷 트위터아이디(@ID)`")
        print(f"https://twitter.com/{twitter_id.replace('@','')}")
        a=await utils.web.async_screenshot(f"https://twitter.com/{twitter_id.replace('@','')}")
        await ctx.send(ctx.author.mention, file=discord.File(a, "screenshot.png"))
    @commands.command(name="정보")
    async def see_info(self, ctx, member: Optional[discord.Member]):
        timestamp = datetime.datetime.utcnow()
        KST = datetime.timedelta(hours=9)
        if not member:
            member = ctx.author
        nick = member.nick
        if not nick:
            nick = member.name
        try:
            dbdoc = self.db.collection(f"users").document(f"{member.id}").get()
            data = dbdoc.to_dict()
            print(data['usertag'])
        except:
            return await ctx.send(f"`{nick}`님은 정보가 등록되어 있지 않습니다.")
        url_tag = data['usertag'].replace("@", "")
        data['usertag'] = data['usertag'].replace('_', "\_")
        
        embed = discord.Embed(
            color=0x123456,
            title=f"{nick} 정보",
            description=f"",
            timestamp=timestamp
        )
        
        embed.add_field(name="트위터 아이디", value=f"[{data['usertag']}](https://twitter.com/{url_tag})\n　")
        embed.add_field(name="\n성별", value=f"{data['introduce']['gender']}\n　")
        embed.add_field(name="\n성향", value=f"{data['introduce']['tend']}\n　")
        embed.add_field(name="\n연령대", value=f"{data['introduce']['age']}\n　")
        await ctx.send(embed=embed)
    @commands.command()
    async def funcname(self, ctx):
        timestamp = datetime.datetime.utcnow()
        KST = datetime.timedelta(hours=9)
        nick = ctx.author.nick
        if not nick:
            nick = ctx.author.name
        embed = discord.Embed(
            color=0x543312,
            title=f"{ctx.author.nick}님의 로그인 링크",
            description=f"[링크](https://{config.site_url}/login?discordId={ctx.author.id}&mode=update)",
            timestamp=timestamp
        )
        await ctx.author.send(embed=embed)
        await ctx.send(f"{ctx.author.mention} 개인DM으로 전송된 링크를 통해 로그인하세요.")
    @commands.command(name="도움말")
    async def help_command(self, ctx):
        text = """```
유저:
    a.정보 (유저이름/멘션)
    a.정보수정 (본인만)
관리자:
    a.강제승인 (유저이름/멘션)
    a.가입링크 (유저이름/멘션)
    a.정보수정 (유저이름/멘션)
    a.승인갯수변경 숫자
```"""
        await ctx.send(text)
    @commands.command(name="정보수정")
    async def register_info(self, ctx, member: Optional[discord.Member]):
        if not member:
            member = ctx.author
        nick = member.nick
        if not nick:
            nick = member.name
        if member != ctx.author:
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send(f"{ctx.author.mention} 님은 다른 유저의 정보를 업데이트 할수 없습니다.")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        await ctx.send(f"`{nick}`님의 정보를 등록합니다. 꼭 주어지는 선택사항 중에 입력하세요.\n1.남자/여자/기타")
        gender_msg = await self.bot.wait_for('message', timeout=120.0, check=check)
        if not (gender_msg.content == "남자" or gender_msg.content == "여자" or gender_msg.content == "기타"):
            return await ctx.send("올바르지 않은 입력입니다. 등록을 취소합니다.")
        await ctx.send(f"2.돔/섭/스위치")
        tend_msg = await self.bot.wait_for('message', timeout=120.0, check=check)
        if not (tend_msg.content == "돔" or tend_msg.content == "섭" or tend_msg.content == "스위치"):
            return await ctx.send("올바르지 않은 입력입니다. 등록을 취소합니다.")
        await ctx.send(f"3.성인/미자")
        age_msg = await self.bot.wait_for('message', timeout=120.0, check=check)
        if not (age_msg.content == "성인" or age_msg.content == "미자"):
            return await ctx.send("올바르지 않은 입력입니다. 등록을 취소합니다.")
        await ctx.send(f"4.트위터 아이디(예:@twitter)")
        tag_msg = await self.bot.wait_for('message', timeout=120.0, check=check)
        if not tag_msg.content.startswith("@"):
            return await ctx.send("올바르지 않은 입력입니다. 등록을 취소합니다. (형식: @your_user_tag)")
        ndata ={"usertag": tag_msg.content,"introduce":{
            "gender": gender_msg.content,
            "tend": tend_msg.content,
            "age": age_msg.content,
            "nickname": nick
        }}
        dbdoc = self.db.collection(f"users").document(f"{member.id}")
        try:
            dbdoc.update(ndata)
        except:
            dbdoc.set(ndata)
        await ctx.send(f"정보 등록 완료!")
        await self.see_info(ctx, member)
    
        
def setup(bot):
    bot.add_cog(UserCog(bot))
