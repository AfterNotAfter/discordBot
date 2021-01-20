import discord
from discord.ext import commands
import traceback
import datetime
import asyncio
import sys
import config
import importlib
import discodo
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import extensions.admin
#https://github.com/kijk2869/discodo/issues/110
class MusicCog(commands.Cog):
    def __init__(self, bot):
        importlib.reload(config)
        self.bot = bot
        #FireBase
        try:
            app = firebase_admin.get_app()
        except ValueError as e:
            cred = credentials.Certificate('./cert/firebasecert.json')
            firebase_admin.initialize_app(cred)
        self.Audio = discodo.DPYClient(bot)
        self.Audio.register_node("localhost", 8000, password="hellodiscodo")
        
        
        self.db = firestore.client()
    def cog_check(self, ctx):
        return True
    async def getDiscodoVC(self, ctx):
        try:
            return self.Audio.getVC(ctx.guild)
        except discodo.errors.VoiceClientNotFound:
            await ctx.send("먼저 `a.입장` 으로 저를 불러주세요!")
            return None
    @commands.command(name="입장",aliases=["연결","join","조인"])
    async def _join(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("음성채널에 먼저 들어가 계세요! ~~제가 씻고 따라 갈게요~~")
        await self.Audio.connect(ctx.author.voice.channel)
        return await ctx.send(f"`{ctx.author.voice.channel.mention}` 방으로 들어갔어요!")

    @commands.command(name="멈춰",aliases=["중지","stop","스탑","퇴장","나가","연결끊기"])
    async def _stop(self, ctx):
        vc = await self.getDiscodoVC(ctx)


        await vc.destroy()
        

        return await ctx.send("음악 재생을 중지했어요! (플레이리스트 비움)")

    @commands.command(name="재생",aliases=["플레이","play"])
    async def _play(self, ctx, *, music):
        vc = await self.getDiscodoVC(ctx)
        if not hasattr(vc, "channel"):
            vc.channel = ctx.channel
        Source = await vc.loadSource(music)
        
        if isinstance(Source, list):
            return await ctx.send(
                f"`{Source[0]['title']}` 빼고 나머지 `{len(Source) - 1}` 곡들을 추가했어요!"
            )
        else:
            return await ctx.send(f"`{Source['data']['title']}` 음악을 추가했어요!")

    @commands.command(name="스킵",aliases=["건너뛰기","skip"])
    async def _skip(self, ctx, offset: int = 1):
        vc = await self.getDiscodoVC(ctx)
        Data = await vc.getState()
        
        return await ctx.send(f"`{Data['current']['title']}` 을 스킵하는중!")

    @commands.command(name="볼륨",aliases=["음량","volume"])
    async def _volume(self, ctx, offset: int = 20):
        vc = await self.getDiscodoVC(ctx)

        Volume = await vc.setVolume(offset/100)

        return await ctx.send(f"볼륨을 {Volume*100}% 로 설정했어요!")
    @commands.command(name="지금",aliases=["np"])
    async def _np(self, ctx):
        vc = await self.getDiscodoVC(ctx)
        State = await vc.getState()
        if len(str(State))<2:
            return await ctx.send("노래를 재생중이지 않습니다!\n`a.재생 (play)` 명령어로 노래를 재생하세요!")
       
        now_r = State["position"]
        dur_r = State["duration"]
        sec = int(now_r % 60)
        min = int(now_r / 60 % 60)
        now = f"{sec}초"
        if now_r >= 60:
            now = f"{min}분 {sec}초"

        sec = int(dur_r % 60)
        min = int(dur_r / 60 % 60)
        dur = f"{sec}초"
        if dur_r >= 60:
            dur = f"{min}분 {sec}초"

        return await ctx.send(
            f"지금 재생중: {State['current']['title']} `{now}:{dur}`"
        )
    @commands.command(name="큐",aliases=["queue","q"])
    async def _queue(self, ctx):
        vc = await self.getDiscodoVC(ctx)
        State = await vc.getState()
        Queue = await vc.getQueue()
        now_r = State["position"]
        dur_r = State["duration"]
        sec = int(now_r % 60)
        min = int(now_r / 60 % 60)
        now = f"{sec}초"
        if now_r >= 60:
            now = f"{min}분 {sec}초"

        sec = int(dur_r % 60)
        min = int(dur_r / 60 % 60)
        dur = f"{sec}초"
        if dur_r >= 60:
            dur = f"{min}분 {sec}초"
        try:
            QueueText = "\n".join(
                [str(Queue.index(Item) + 1) + ". " + Item['title'] for Item in Queue]
            )

            return await ctx.send(
                f"""
    지금 재생중: {State['current']['title']} `{now}:{dur}`

    {QueueText}
    """
            )
        except Exception as e:
            print(e)
            return await ctx.send(
                f"""
    재생 대기목록이 비어있습니다!\n`a.재생 (play)` 명령어로 노래를 추가하세요!
    """
            )
    @commands.command(name="자동재생",aliases=["autoplay","오토플레이"])
    async def _autoplay(self, ctx, offset: str = "on"):
        vc = await self.getDiscodoVC(ctx)

        offset = {"on": True, "off": False}.get(offset, True)

        autoplay = await vc.setAutoplay(offset)

        return await ctx.send(
            f'자동재생이 {"켜졌습니다!" if autoplay else "꺼졌습니다!"}.'
        )

    @commands.command(name="크로스페이드")
    async def _crossfade(self, ctx, offset: int = 3):
        vc = await self.getDiscodoVC(ctx)
        print(offset)
        Crossfade = await vc.setCrossfade(int(offset))

        return await ctx.send(f"크로스페이드를 {Crossfade} 초로 설정했어요!")

    

'''
    @commands.command(name="seek")
    async def _seek(self, ctx, offset: int = 1):
        vc = self.Audio.getVC(ctx.guild.id, safe=True)

        if not vc:
            return await ctx.send("Please type `!join` first.")

        await vc.seek(offset)

        return await ctx.send(f"Seek to {offset}.")
'''


def setup(bot):
    bot.add_cog(MusicCog(bot))
