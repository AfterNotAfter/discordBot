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
class UserCog(commands.Cog):
    def __init__(self, bot):
        importlib.reload(config)
        #FireBase
        try:
            app = firebase_admin.get_app()
        except ValueError as e:
            cred = credentials.Certificate('./cert/firebasecert.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://leobot-9fbb1.firebaseio.com/'
        })
        
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

    
        
def setup(bot):
    bot.add_cog(UserCog(bot))
