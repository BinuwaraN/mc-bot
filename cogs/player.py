import json
import discord
import logging
from discord.ext import commands
import asyncio
import aiohttp
import asyncio
import logging
import base64

import classyjson as cj
import arrow

from bot_errors import *

log = logging.getLogger("bot")


class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ses = aiohttp.ClientSession(loop=bot.loop)

    @commands.command(name="mcprofile", aliases=["minecraftprofile", "nametouuid", "uuidtoname", "mcp"])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def minecraft_profile(self, ctx, player):

        if 17 > len(player) > 1 and player.lower().strip('abcdefghijklmnopqrstuvwxyz1234567890_') == '':
            with ctx.typing():
                res = await self.ses.get(f'https://api.mojang.com/users/profiles/minecraft/{player}')

            if res.status == 204:
                await ctx.send('Ding dong! That player is invalid or doesn\'t exist.')
                return
            elif res.status != 200:
                await ctx.send('Something went wrong while fetching that user\'s profile...')
                return

            jj = await res.json()
            uuid = jj['id']
        elif len(player) in (32, 36,) and player.lower().strip('abcdefghijklmnopqrstuvwxyz1234567890-') == '':  # player is a uuid
            uuid = player.replace('-', '')
        else:
            await ctx.send('Ding dong! That player is invalid or doesn\'t exist.')
            return

        with ctx.typing():
            resps = await asyncio.gather(
                self.ses.get(
                    f'https://api.mojang.com/user/profiles/{uuid}/names'),
                self.ses.get(
                    f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid}')
            )

        for res in resps:
            if res.status == 204:
                await ctx.send('Ding dong! That player is invalid or doesn\'t exist.')
                return
            elif res.status != 200:
                await ctx.send('Something went wrong while fetching that user\'s profile...')
                return

        names = cj.classify(await resps[0].json())
        profile = cj.classify(await resps[1].json())

        skin_url = None
        cape_url = None

        for prop in profile['properties']:
            if prop['name'] == 'textures':
                textures = cj.loads(base64.b64decode(prop['value'])).textures
                skin_url = textures.get('SKIN', {}).get('url')
                cape_url = textures.get('CAPE', {}).get('url')
                break

        name_hist = '\uFEFF'

        for i, name in enumerate(reversed(names)):
            time = name.get('changedToAt')

            if time is None:
                time = 'first username'
            else:
                time = arrow.Arrow.fromtimestamp(time)
                time = time.format('MMM D, YYYY', locale='en') + \
                    ', ' + time.humanize(locale='en')

            name_hist += f'**{len(names)-i}.** `{name.name}` - {time}\n'

        embed = discord.Embed(color=discord.Color.green(
        ), title='Minecraft profile for `{}`'.format(profile.name))

        if skin_url is not None:
            embed.description = f'[**Skin Download**]({skin_url})'

        if cape_url is not None:
            embed.description += f' | [**Cape Download**]({cape_url})'

        embed.set_thumbnail(
            url=f'https://visage.surgeplay.com/head/{uuid}.png')

        embed.add_field(
            name=':link: UUID', value=f'`{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}`\n`{uuid}`', inline=False)
        embed.add_field(name=(':label: ' + 'Name History'),
                        value=name_hist, inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Player(bot))
