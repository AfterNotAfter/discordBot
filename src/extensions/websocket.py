import discord
from discord.ext import commands
import asyncio
import websockets
from urllib.parse import urlparse, parse_qs
import os
import platform
import jwt
import config
import utils
import traceback
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import importlib
class ApiSocketCog(commands.Cog):
    def __init__(self, bot):
        importlib.reload(config)
        self.bot=bot
        asyncio.get_event_loop().create_task(self.start_ws())
        self.logger = bot.logger
        #FireBase
        try:
            app = firebase_admin.get_app()
        except ValueError as e:
            cred = credentials.Certificate('./cert/firebasecert.json')
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()

    def cog_unload(self):
        self.ws.close()

    async def start_ws(self):
        self.ws = await websockets.serve(self.accept, None, 3000)

    async def setting_user(self, data):
        new_user_channel = self.bot.get_channel(config.discord_new_user_channel)
        introduce_channel = self.bot.get_channel(config.discord_introduce_channel)
        guild = new_user_channel.guild
        member = await guild.fetch_member(data['discordId'])
        male_role = guild.get_role(config.discord_male_role)
        female_role = guild.get_role(config.discord_female_role)
        adult_role = guild.get_role(config.discord_adult_role)
        teen_role = guild.get_role(config.discord_teen_role)
        dom_role = guild.get_role(config.discord_dom_role)
        sub_role = guild.get_role(config.discord_sub_role)
        swt_role = guild.get_role(config.discord_swt_role)

        give_roles=[]
        nickname = data['introduce']['nickname']
        age = data['introduce']['age']
        gender = data['introduce']['gender']
        tend = data['introduce']['tend']

        

        if age == "미자":
            give_roles.append(teen_role)
        elif age == "성인":
            give_roles.append(adult_role)
        if gender == "남자":
            give_roles.append(male_role)
        elif gender == "여자":
            give_roles.append(female_role)
        if tend == "돔":
            give_roles.append(dom_role)
        elif tend == "섭":
            give_roles.append(sub_role)
        elif tend == "스위치":
            give_roles.append(swt_role)
        try:
            await member.edit(nick=nickname)
        except:
            pass
        for role in give_roles:
            await member.add_roles(role)
        data['usertag'] = data['usertag'].replace('_',"\_")
        send_text = f"{member.mention} | {gender} | {tend} | {age} | {data['usertag']}"
        send_text.replace("_","\_")
        await introduce_channel.send(send_text)
        if data['mode'] == "register":
            await new_user_channel.send(f"{member.mention} 계정 인증 및 자기소개 등록 완료! 가입심사 통과까지 기다려주세요!")
    async def give_user_role(self,data):
        log_channel = self.bot.get_channel(config.discord_log_channel)
        user_role = log_channel.guild.get_role(config.discord_user_role)
        member = await log_channel.guild.fetch_member(data['discordId'])
        dbdoc = self.db.collection(f"config").document(f"original_user").get()
        data = dbdoc.to_dict()
        if member.id in data['id']:
            await member.add_roles(user_role,reason="기존유저")
    async def send_message(self, data):
        verify_channel = self.bot.get_channel(config.discord_verify_channel)
        url=f"https://twitter.com/{data['usertag'].replace('@','')}"
        print(url)
        self.logger.info(f"{url} <- 스크린샷")
        a = await utils.web.async_screenshot(url)
        msg = await verify_channel.send(f"@everyone\n\n<@{data['discordId']}> 님의 트위터 아이디는 {data['usertag']} 입니다.\n찬성하시는 분은 :+1: 반대하시는분은 :x: 이모지를 달아주세요.", file=discord.File(a, "screenshot.png"))
        print(msg)
        await msg.add_reaction("👍")
        await msg.add_reaction("❌")
        
    async def accept(self, websocket: websockets.WebSocketServerProtocol, path):
        query = parse_qs(urlparse(path).query)
        token = query.get('auth')
        
        ip = websocket.remote_address[0] if websocket.remote_address else None
        
        self.logger.info(f"WEBSOCKET: {ip} 연결 성공")
        while not websocket.closed:
            try:
                data = await websocket.recv()
            except websockets.ConnectionClosedError as e:
                if e.code == 1005:
                    break
                else:
                    self.logger.info(f'WEBSOCKET: 연결이 오류와 함께 닫혔습니다: {e}')
            except websockets.exceptions.ConnectionClosedOK as e:
                self.logger.info(f'WEBSOCKET: 연결이 정상적으로 닫혔습니다: {e}')
            else:
                print(data)
                try:
                    data = jwt.decode(data, config.site_url,algorithms="HS256")
                    
                    print(data)
                    await self.setting_user(data)
                    if data['mode'] == "register":
                        await self.send_message(data)
                    if data['mode'] == "update":
                        await self.give_user_role(data)
                    await websocket.send("OK")
                except:
                    tb=traceback.format_exc()
                    await websocket.send(tb)

def setup(bot):
    bot.add_cog(ApiSocketCog(bot))