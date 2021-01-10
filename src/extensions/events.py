import discord
from discord.ext import commands
import traceback
import datetime
import asyncio
import sys
import config

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener('on_member_join')
    async def member_join(self, member: discord.Member):
        timestamp = datetime.datetime.utcnow()
        KST = datetime.timedelta(hours=9)
        hello_channel = self.bot.get_channel(config.discord_new_user_channel)
        admin_role = member.guild.get_role(config.discord_admin_role)
        if member == member.guild.me:
            return
        
        hi_embed = discord.Embed(color=0x00f1ff, title=f'{member}님이 들어오셨어요!', description=f'`{member.guild}`에 오신걸 환영합니다!\n',
                    timestamp=timestamp)
        hi_embed.set_thumbnail(url=f"{str(member.avatar_url)}")
        hi_embed.add_field(name='유저태그', value=f'{member}', inline=True)
        hi_embed.add_field(name='계정 생성일', value=f'{str(member.created_at + KST)[:-10]}', inline=True)
        
        hi_embed.set_footer(text="꼭 #신입공지를 읽어주세요!")
        await hello_channel.send(member.mention, embed=hi_embed)
        secret_embed = discord.Embed(
            color=0x7be53b,
            title="{member}님의 고유 인증 링크",
            description=f"[링크](https://{config.site_url}/login?discordId={member.id})",
            timestamp=timestamp
            )
        try:
            await member.send(embed=secret_embed)
        except:
            await hello_channel.send('이 유저는 개인DM을 막아두어서 유저 인증 고유 링크를 보내지 못하였습니다.\n {admin_role.mention} 분들 께서 고유링크를 생성해 전달해 주세요!')
    @commands.Cog.listener('on_member_remove')
    async def member_leave(self,member: discord.Member)


def setup(bot):
    bot.add_cog(Events(bot))