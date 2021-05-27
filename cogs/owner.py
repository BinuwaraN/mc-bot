import discord
from discord.ext import commands


class Owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='say')
    @commands.is_owner()
    async def say_text(self, ctx, *, _text):
        """Sends whatever is put into the command"""

        await ctx.send(_text)

    @commands.command(pass_context=True, name='test')
    @commands.is_owner()
    async def test(self, ctx):
        """
        Checks if the bot is alive.
        """
        await ctx.send('I\'m here you ding dong')

    @commands.command(pass_context=True, name='setpfp')
    @commands.is_owner()
    async def profile(self, ctx, url):
        """
        Change bot profile picture
        """
        async with self.bot.http_session.get(url) as resp:
            bytes_ = await resp.read()
            await self.bot.user.edit(avatar=bytes_)
        emb = discord.Embed(colour=discord.Color.green(),
                            title='Profile picture changed successfully')
        emb.set_thumbnail(url=url)
        await ctx.send(embed=emb)

    @commands.command(name="purge")
    @commands.is_owner()
    async def purge(self, ctx, number: int):
        """
        Purge messages
        """
        await ctx.message.channel.purge(limit=number + 1)


def setup(bot):
    bot.add_cog(Owner(bot))
