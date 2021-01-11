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
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://leobot-9fbb1.firebaseio.com/'
        })
        
        self.db = firestore.client()

    def cog_unload(self):
        self.ws.close()

    async def start_ws(self):
        self.ws = await websockets.serve(self.accept, None, 3000)


    async def send_message(self, data):
        verify_channel = self.bot.get_channel(config.discord_verify_channel)
        print(f"https://twitter.com/{data['usertag'].replace('@','')}")
        a = await utils.web.async_screenshot(f"https://twitter.com/{data['usertag'].replace('@','')}")
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
                    await websocket.send("OK")
                    print(data)
                    await self.send_message(data)
                except:
                    tb=traceback.format_exc()
                    await websocket.send(tb)

def setup(bot):
    bot.add_cog(ApiSocketCog(bot))