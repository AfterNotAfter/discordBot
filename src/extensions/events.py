import discord
from discord.ext import commands
import traceback
import datetime
import asyncio
import sys
import config

class EventsCog(commands.Cog):
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
        hi_embed.add_field(name='유저태그', value=f'{member}', inline=False)
        hi_embed.add_field(name='계정 생성일', value=f'{str(member.created_at + KST)[:-10]}', inline=False)
        hi_embed.add_field(name='**안내**', value=f'개인 메세지(DM)으로 전송된 인증링크를 통해 인증해주세요!', inline=False)
        hi_embed.set_footer(text="꼭 #신입공지를 읽어주세요!")
        await hello_channel.send(member.mention, embed=hi_embed)
        secret_embed = discord.Embed(
            color=0x7be53b,
            title=f"{member}님의 고유 인증 링크",
            description=f"[링크](https://{config.site_url}/login?discordId={member.id})",
            timestamp=timestamp
            )
        try:
            await member.send(embed=secret_embed)
        except:
            await hello_channel.send('이 유저는 개인DM을 막아두어서 유저 인증 고유 링크를 보내지 못하였습니다.\n {admin_role.mention} 분들 께서 고유링크를 생성해 전달해 주세요!')

    @commands.Cog.listener('on_member_remove')
    async def member_leave(self, member: discord.Member):
        KST = datetime.timedelta(hours=9)
        timestamp = datetime.datetime.utcnow()
        hello_channel = self.bot.get_channel(config.discord_new_user_channel)

        bye_embed = discord.Embed(color=0xFF69B4, title=f'{member}님이 나가셨어요..',
                            description=f'서버: `{member.guild}`',
                            timestamp=timestamp)
        bye_embed.add_field(name='유저태그', value=f'{member}', inline=True)
        bye_embed.set_thumbnail(url=f"{str(member.avatar_url)}")
        bye_embed.add_field(name='계정 생성일', value=f'{str(member.created_at + KST)[:-10]}', inline=False)
        bye_embed.add_field(name='서버 참가일', value=f'{str(member.joined_at + KST)[:-10]}', inline=False)

        await hello_channel.send(embed=bye_embed)

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        log_channel = self.bot.get_channel(config.discord_log_channel)
        user_role = message.guild.get_role(config.discord_user_role)
        emoji = payload.emoji
        is_thumbsup = str(emoji) == "👍" 
        is_x = str(emoji) == "❌"
        if is_thumbsup or is_x:
            if channel.id == config.discord_verify_channel:
                member = message.mentions[0]
                reactions = message.reactions
                thumbsup_reaction = reactions[0]
                x_reaction = reactions[1]
                if is_thumbsup:
                    await log_channel.send(f"{payload.member.mention} 님이 👍으로 {member.mention} 님의 가입에 동의하셨습니다.")
                if is_x:
                    await log_channel.send(f"{payload.member.mention} 님이 ❌으로 {member.mention} 님의 가입에 반대하셨습니다.")

                if thumbsup_reaction.count >= config.discord_agree_count:
                    agreed_users = []
                    agreed_users_mention =""
                    async for user in thumbsup_reaction.users():
                        if not user == self.bot.me:
                            agreed_users.append(user)
                            agreed_users_mention += f"{user.mention} "

                    disagreed_users = []
                    disagreed_users_mention =""
                    async for user in x_reaction.users():
                        if not user == self.bot.me:
                            disagreed_users.append(user)
                            disagreed_users_mention += f"{user.mention} "

                    if x_reaction.count < 2:
                        await log_channel.send(f"{member.mention}님의 가입을 승인하였습니다!\n 동의자 목록: {agreed_users_mention}")
                        await member.add_roles(user_role,reason="자동 가입 승인.")
                    else:
                        await log_channel.send(f"비동의자가 있기 때문에, {member.mention}님의 가입을 승인하지 않았습니다.\n 동의자 목록: {agreed_users_mention}\n\n 비동의자 목록: {disagreed_users_mention}")

        else:
            return

def setup(bot):
    bot.add_cog(EventsCog(bot))