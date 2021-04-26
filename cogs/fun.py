from urllib.parse import quote as urlquote
from discord.ext import commands
import classyjson as cj
import discord
import aiohttp
import random
import typing

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ses = aiohttp.ClientSession(loop=bot.loop)

    @commands.command(name='achievement', aliases=['mcachieve'])
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def minecraft_achievement(self, ctx, *, text):
        url = f'https://api.iapetus11.me/mc/achievement/{urlquote(text[:26])}'
        embed = discord.Embed(color=discord.Color.green())

        embed.description = '[**[Download Image]**]({})'.format(url)
        embed.set_image(url=url)

        await ctx.send(embed=embed)

    @commands.command(name='kill', aliases=['die', 'kil', 'dorito'])
    async def kill_thing(self, ctx, *, thing: typing.Union[discord.Member, str]):
        killMessages = ['**{0}** was suicided',
                        '**{0}** died by death',
                        '**{0}** died by fall damage',
                        '**{0}** dug straight down',
                        '**{0}** was killed by **{1}**',
                        '**{0}** choked on a dorito and died',
                        '**{0}** was killed in a tragic accident involving doritos and **{1}**',
                        'We regret to inform you, **{0}** has been died',
                        '**{0}** is now dead.',
                        'A creeper blew up **{0}**',
                        '**{0}** suicided by creeper',
                        '**{0}** was yeeted into the void',
                        '**{0}** was yeeted into the void by an enderman',
                        '**{0}** fell into lava',
                        '**{0}** was smited by Villager Bot',
                        '**{0}** was yeeted into the void by **{1}**',
                        '**{0}** exploded in the microwave',
                        '**{0}** was cut in half to demonstrate the power of flex tape',
                        '**{0}** was yeeted across the map by a creeper',
                        '**{0}** was bonked by **{1}**']

        if isinstance(thing, discord.Member):
            thing = thing.mention

        em = discord.Embed(
            description=random.choice(killMessages).format(
                thing[:500], ctx.author.mention),
            color=discord.Color.green(),
        )

        return await ctx.send(embed=em)
        
def setup(bot):
    bot.add_cog(Fun(bot))
