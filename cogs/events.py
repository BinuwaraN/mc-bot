from bot_errors import NoPermissionError
from discord.ext import commands
import traceback
import discord
import random
import sys
import logging

log = logging.getLogger("bot")


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.bg_task = self.bot.loop.create_task(self.my_background_task())

    # async def my_background_task(self):
    #     await self.wait_until_ready()
    #     counter = 0
    #     channel = self.get_channel(767537970348818456)  # channel ID goes here
    #     while not self.is_closed():
    #         counter += 1
    #         await channel.send(counter)
    #         await asyncio.sleep(5)  # task runs every 60 seconds

    @commands.Cog.listener()
    async def on_message(self, m):
        # e = Emojize()
        if m.author.bot:
            return

        if "good" in m.content.lower() and "bot" in m.content.lower():
            destination = None

            if m.guild is None:
                destination = "Private Message"
            else:
                destination = f"#{m.channel} ({m.guild})"

            log.info(f"{m.author} in {destination}: {m.content}")
            await m.channel.send(random.choice(['😊', '😎', '{} is the best 😁'.format(m.author.name)]))

        # if '!play' in m.content.lower():
        #     destination = None

        #     if m.guild is None:
        #         destination = "Private Message"
        #     else:
        #         destination = f"#{m.channel} ({m.guild})"

        #     log.info(f"{m.author} in {destination}: {m.content}")

        #     await m.channel.send('I can play music too (with highest quality possible), `.play [url or name]` :notes:. \nFor more info type `.help Music` :musical_note:')

        # if 'new year' in m.content.lower() or 'happy year' in m.content.lower() in m.content.lower() and 'bot' in m.content.lower():
        #     em = discord.Embed(
        #         title='Same to you!',
        #         color=discord.Color.dark_teal(),
        #     )
        #     em.set_footer(text='Beep Boop')
        #     em.set_thumbnail(
        #         url="https://media.giphy.com/media/2tKbpTlzGeXYp7rmlS/giphy.gif")
        #     await m.reply(embed=em)

        if "bad bot" in m.content.lower():
            destination = None

            if m.guild is None:
                destination = "Private Message"
            else:
                destination = f"#{m.channel} ({m.guild})"

            log.info(f"{m.author} in {destination}: {m.content}")
            await m.channel.send('😥')

    async def send_unexpected_error(self, ctx, error):
        em = discord.Embed(
            title=":warning: Unexpected Error",
            color=discord.Color.gold(),
        )

        description = (
            "An unexpected error has occured:"
            f"```py\n{error}```\n"
        )

        em.description = description
        await ctx.send(embed=em)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == 235088799074484224:
            pass
            # await member.move_to(None)
            # log.info(f"Removed {member.name} from the voice channel")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log.info(f'{member.id} joined the server')
        welcome_messages = [
            f'Brace yourselves. {member.name} just joined the server.',
            f'Challenger approaching - {member.name} has appeared',
            f'Welcome {member.name}>. Leave your weapon by the door.',
            f'Big {member.name} showed up!',
            f'{member.name} just joined... or did they?',
            f'Ready player {member.name}>',
            f'{member.name} hopped into the server. Kangaroo!!',
            f'{member.name} joined. You must construct additional pylons.',
            f'Hello. Is it {member.name} you\'re looking for?',
            f'Where\'s {member.name} in the server!',
            f'It\'s dangerous to go alone, take {member.name}',
        ]
        # channel = self.bot.get_channel(767537970348818456)
        channel = self.bot.get_channel(789243692887572535)

        url = 'https://cdn.discordapp.com/attachments/727135407627698177/832940573555687444/Vibe_Check_to_enter_Whole_-_Copy.png'
        embed = discord.Embed(color=discord.Color.green())

        embed.title = random.choice(welcome_messages)
        # embed.set_image(url=url)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        red_tick = "\N{CROSS MARK}"

        if hasattr(ctx, "handled"):
            return

        if isinstance(error, commands.NoPrivateMessage):
            message = await ctx.send(
                f"{red_tick} This command can't be used in DMs."
            )

        if hasattr(error, 'original'):
            if isinstance(error.original, NoPermissionError):
                message = await ctx.send('You don\'t have permission for that cool command.')

        elif isinstance(error, commands.ArgumentParsingError):
            message = await ctx.send(f"{red_tick} {error}")

        elif isinstance(error, commands.CommandOnCooldown):
            message = await ctx.send(
                f"{red_tick} You are on cooldown. Try again in {int(error.retry_after)} seconds."
            )

        elif isinstance(error, commands.errors.BotMissingPermissions):
            perms = ""

            for perm in error.missing_perms:
                formatted = (
                    str(perm).replace("_", " ").replace(
                        "guild", "server").capitalize()
                )
                perms += f"\n- `{formatted}`"

            message = await ctx.send(
                f"{red_tick} I am missing some required permission(s):{perms}"
            )

        elif isinstance(error, commands.errors.BadArgument):
            message = await ctx.send(f"{red_tick} {error}")

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            message = await ctx.send(
                f"{red_tick} Missing a required argument: `{error.param.name}`"
            )

        elif (
            isinstance(error, commands.CommandInvokeError)
            and str(ctx.command) == "help"
        ):
            pass

        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            # if True: # for debugging
            if not isinstance(original, discord.HTTPException):
                print(
                    "Ignoring exception in command {}:".format(ctx.command),
                    file=sys.stderr,
                )
                traceback.print_exception(
                    type(error), error, error.__traceback__, file=sys.stderr
                )

                await self.send_unexpected_error(ctx, error)
                return

    # async def my_background_task(self):
    #     await self.wait_until_ready()
    #     counter = 0
    #     channel = self.get_channel(788174826942627872)

    #     while not self.is_closed():
    #         print(datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p'))

    #         if datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p') == "01/01/2021 12:00 PM":
    #             em = discord.Embed(
    #                 title='Ding Dong! Happy New Year 🎉🎉',
    #                 description='Wishing you all 12 months of success, 52 weeks of laughter, 365 days of fun, 8,760 hours of joy, 525,600 minutes of good luck, and 31,536,000 seconds of happiness.',
    #                 color=discord.Color.dark_magenta(),
    #             )
    #             em.set_thumbnail(
    #                 url="https://media.giphy.com/media/41rZXFMXKqeTvDFwEB/giphy.gif")

    #             em.set_footer(text='Beep Boop')
    #             await channel.send('@everyone')
    #             await channel.send(embed=em)
    #             await self.stop()
    #         await asyncio.sleep(5)


def setup(bot):
    bot.add_cog(Events(bot))
