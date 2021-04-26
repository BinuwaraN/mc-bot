from bot_errors import NotOnServerError
import discord
from discord.ext import commands
from bot_errors import NoPermissionError
import aiohttp


def check_mod(user, admin_users):
    try:
        for userid in admin_users:
            if str(user.id) in str(userid):
                return True
    except AttributeError:
        raise NotOnServerError

    return False


class Owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot
        self.ses = aiohttp.ClientSession(loop=bot.loop)
        self.owners = self.bot.config["owners"]

    @commands.command(name='say')
    async def say_text(self, ctx, *, _text):
        """Sends whatever is put into the command"""
        if check_mod(ctx.message.author, self.bot.config["owners"]):
            try:
                await ctx.message.delete()
            except Exception:
                pass
        else:
            raise NoPermissionError

        await ctx.send(_text)

    @commands.command(pass_context=True, name='test')
    async def test(self, ctx):
        """
        Checks if the bot is alive.
        """
        if check_mod(ctx.message.author, self.bot.config["owners"]):
            await ctx.send('I\'m here you ding dong')
        else:
            raise NoPermissionError

    @commands.command(pass_context=True, name='setpfp')
    @commands.is_owner()
    async def profile(self, ctx, url):
        if check_mod(ctx.message.author, self.bot.config["owners"]):
            async with self.ses.get(url) as resp:
                bytes_ = await resp.read()
                await self.bot.user.edit(avatar=bytes_)

            emb = discord.Embed(colour=discord.Color.green(),
                                title='Profile picture changed successfully')
            emb.set_thumbnail(url=url)
            await ctx.send(embed=emb)
        else:
            raise NoPermissionError

    @commands.command(name="purge")
    @commands.is_owner()
    async def purge(self, ctx, number: int):
        # if check_mod(ctx.message.author, self.bot.config["owners"]):
        purged_messages = await ctx.message.channel.purge(limit=number + 1)
        # embed = discord.Embed(
        #     title="Chat Cleared!",
        #     description=f"**{crx.message.author}** cleared **{len(purged_messages)}** messages!",
        #     color=0x00FF00
        # )
        # await ctx.send(embed=embed)
        # else:
        #     raise NoPermissionError
        # embed = discord.Embed(
        #     title="Error!",
        #     description="You don't have the permission to use this command.",
        #     color=0x00FF00
        # )
        # await context.send(embed=embed)

def setup(bot):
    bot.add_cog(Owner(bot))
