import json
import logging
import logging.config
import os
import config
import discord
from discord.ext import commands

import extensions.api
from multiprocessing import Process, Queue
with open("logging.json") as f:
    logging.config.dictConfig(json.load(f))




class DiscordBot(commands.Bot):
    extension_list = ["extensions.admin","extensions.websocket","extensions.events","extensions.moderator","extensions.user"]

    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user}")

    async def on_error(self, event, *args, **kwargs):
        self.logger.exception("")

    def __init__(self, logger,intents):
        super().__init__(commands.when_mentioned_or("a."),intents=intents)
        self.logger = logger
        
        for ext in self.extension_list:
            self.load_extension(ext)

if __name__ == "__main__":
    th1 = Process(target=extensions.api.Webserver)
    th1.start()
    intents = discord.Intents.all()
    bot = DiscordBot(logger=logging.getLogger("bot"),intents=intents)
    
    bot.run(config.bot_token)

    