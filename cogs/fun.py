import os
import discord
import aiohttp
import random
import typing

from urllib.parse import quote as urlquote
from discord.ext import commands

from discord_slash import cog_ext

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ses = aiohttp.ClientSession(loop=bot.loop)

        self.kill_mes = self.load_from_file("kill")

    @staticmethod
    def load_from_file(file: str) -> typing.List[str]:
        """Load text from file.
        Args:
            file (str): file name
        Returns:
            List[str]: list of input
        """
        fileDir = os.path.dirname(os.path.realpath('__file__'))

        filename = os.path.join(fileDir, "resources", f"{file}.txt")
        with open(filename) as f:
            content = f.readlines()
        return [x.strip() for x in content]

    @commands.command()
    async def creeper(self, ctx) -> None:
        """Aw man."""
        
        await ctx.send("Aw man")
    
    @cog_ext.cog_slash(name="creeper")
    async def slash_creeper(self, ctx):
        """Aw man."""
        await ctx.defer()
        await self.creeper(ctx)

    @commands.command(name='kill', aliases=['die', 'kil', 'dorito'])
    async def kill_thing(self, ctx, *, thing: typing.Union[discord.Member, str]):
        """
        Kill that pesky friend in a fun and stylish way.
        """

        if isinstance(thing, discord.Member):
            thing = thing.mention

        await ctx.send(random.choice(self.kill_mes).replace("member", thing))


def setup(bot):
    bot.add_cog(Fun(bot))
