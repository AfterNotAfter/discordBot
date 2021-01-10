import discord
from discord.ext import commands
import asyncio
import websockets
from urllib.parse import urlparse, parse_qs
import os
import platform
import jwt
import config
class ApiSocket(commands.Cog):
    def __init__(self, bot):
        
        self.bot=bot
        asyncio.get_event_loop().create_task(self.start_ws())
        self.logger = bot.logger

    def cog_unload(self):
        self.ws.close()

    async def start_ws(self):
        self.ws = await websockets.serve(self.accept, None, 3000)

            

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
                    data = jwt.decode(data, config.site_url)
                    await websocket.send("OK")
                    print(data)
                except:
                    await websocket.send(data)

def setup(bot):
    cog = ApiSocket(bot)
    bot.add_cog(cog)