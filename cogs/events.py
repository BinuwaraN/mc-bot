from utils.chat_formatting import box, format_perms_list, humanize_timedelta, inline, pagify
from discord.ext import commands
import traceback
import discord
import random
import logging

log = logging.getLogger("bot")


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_channel = self.bot.config["error-channel"]
        # self.bg_task = self.bot.loop.create_task(self.my_background_task())

    @commands.Cog.listener()
    async def on_message(self, m):
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
        channel = self.bot.get_channel(789243692887572535)

        url = 'https://cdn.discordapp.com/attachments/727135407627698177/832940573555687444/Vibe_Check_to_enter_Whole_-_Copy.png'
        embed = discord.Embed(color=discord.Color.green())

        embed.title = random.choice(welcome_messages)
        # embed.set_image(url=url)

        await channel.send(embed=embed)

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

    @staticmethod
    async def handle_check_failure(ctx: commands.Context, e) -> None:
        """
        Send an error message in `ctx` for certain types of CheckFailure.
        The following types are handled:
        * BotMissingPermissions
        * BotMissingRole
        * BotMissingAnyRole
        * NoPrivateMessage
        * InWhitelistCheckFailure
        """
        bot_missing_errors = (
            commands.errors.MissingPermissions,
            commands.errors.MissingRole,
            commands.errors.MissingAnyRole,
        )

        if isinstance(e, bot_missing_errors):
            missing = [
                perm.replace("_", " ").replace("guild", "server").title()
                for perm in e.missing_perms
            ]
            if len(missing) > 2:
                fmt = f"{'**, **'.join(missing[:-1])}, and {missing[-1]}"
            else:
                fmt = " and ".join(missing)
            if len(missing) > 1:
                await ctx.send(
                    (
                        "Sorry, it looks like you don't have the **{fmt}** perm"
                        "missions I need to do that."
                    ).format(fmt=fmt)
                )
            else:
                await ctx.send(
                    (
                        "Sorry, it looks like you don't have the **{fmt}** per"
                        "missions I need to do that."
                    ).format(fmt=fmt)
                )

    @commands.Cog.listener("on_slash_command_error")
    async def on_slash_command_error(self, ctx, ex) -> None:
        await self.handle_check_failure(ctx, ex)

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx, error, unhandled_by_cog=False):  # noqa: C901
        if not unhandled_by_cog:
            if hasattr(ctx.command, "on_error"):
                return

            if ctx.cog:
                if (
                    commands.Cog._get_overridden_method(
                        ctx.cog.cog_command_error)
                    is not None
                ):
                    return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.ArgumentParsingError):
            msg = ("`{user_input}` is not a valid value for `{command}`").format(
                user_input=error.user_input, command=error.cmd
            )
            if error.custom_help_msg:
                msg += f"\n{error.custom_help_msg}"
            await ctx.send(msg)
            if error.send_cmd_help:
                await ctx.send_help(ctx.command)
        elif isinstance(error, commands.ConversionError):
            if error.args:
                await ctx.send(error.args[0])
            else:
                await ctx.send_help(ctx.command)
        elif isinstance(error, commands.UserInputError):
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.BotMissingPermissions):
            if bin(error.missing.value).count("1") == 1:  # Only one perm missing
                msg = (
                    "I require the {permission} permission to execute that command."
                ).format(permission=format_perms_list(error.missing))
            else:
                msg = (
                    "I require {permission_list} permissions to execute that command."
                ).format(permission_list=format_perms_list(error.missing))
            await ctx.send(msg)
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(("That command is not available in DMs."))
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(("That command is only available in DMs."))
        elif isinstance(error, commands.CheckFailure):
            await self.handle_check_failure(ctx, error)
        elif isinstance(error, commands.CommandOnCooldown):
            # if self.bot._bypass_cooldowns and ctx.author.id in self.bot.owner_ids:
            #     ctx.command.reset_cooldown(ctx)
            #     new_ctx = await self.bot.get_context(ctx.message)
            #     await self.bot.invoke(new_ctx)
            #     return
            if delay := humanize_timedelta(seconds=error.retry_after):
                msg = ("This command is on cooldown. Try again in {delay}.").format(
                    delay=delay
                )
            else:
                msg = ("This command is on cooldown. Try again in 1 second.")
            await ctx.send(msg, delete_after=error.retry_after)
        elif isinstance(error, commands.MaxConcurrencyReached):
            if error.per is commands.BucketType.default:
                if error.number > 1:
                    msg = (
                        "Too many people using this command."
                        " It can only be used {number} times concurrently."
                    ).format(number=error.number)
                else:
                    msg = (
                        "Too many people using this command."
                        " It can only be used once concurrently."
                    )
            elif error.per in (commands.BucketType.user, commands.BucketType.member):
                if error.number > 1:
                    msg = (
                        "That command is still completing,"
                        " it can only be used {number} times per {type} concurrently."
                    ).format(number=error.number, type=error.per.name)
                else:
                    msg = (
                        "That command is still completing,"
                        " it can only be used once per {type} concurrently."
                    ).format(type=error.per.name)
            else:
                if error.number > 1:
                    msg = (
                        "Too many people using this command."
                        " It can only be used {number} times per {type} concurrently."
                    ).format(number=error.number, type=error.per.name)
                else:
                    msg = (
                        "Too many people using this command."
                        " It can only be used once per {type} concurrently."
                    ).format(type=error.per.name)
            await ctx.send(msg)
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.errors.HTTPException):
                if error.original.code == 50035:
                    await ctx.send("Invalid input, too long.")
                    return

            log.exception(
                "Exception in command '{}'".format(ctx.command.qualified_name),
                exc_info=error.original,
            )

            message = (
                "Error in command '{command}'. It has "
                "been recorded and should be fixed soon."
            ).format(command=ctx.command.qualified_name)
            exception_log = "Exception in command '{}'\n" "".format(
                ctx.command.qualified_name
            )
            exception_log += "".join(
                traceback.format_exception(
                    type(error), error, error.__traceback__)
            )
            self.bot._last_exception = exception_log
            await ctx.send(inline(message))
            destination = self.bot.get_channel(self.error_channel)
            embed = discord.Embed(title="Bug", color=discord.Color.red())

            embed.set_author(name=str(ctx.author),
                             icon_url=ctx.author.avatar_url)
            embed.add_field(name="Command", value=ctx.command)
            embed.timestamp = ctx.message.created_at

            if ctx.guild is not None:
                embed.add_field(
                    name="Server",
                    value=f"{ctx.guild.name} (ID: {ctx.guild.id})",
                    inline=False,
                )

            embed.add_field(
                name="Channel",
                value=f"{ctx.channel} (ID: {ctx.channel.id})",
                inline=False,
            )
            embed.set_footer(text=f"Author ID: {ctx.author.id}")

            await destination.send(embed=embed)

            for page in pagify(self.bot._last_exception, shorten_by=10):
                try:
                    await destination.send(box(page, lang="py"))
                except discord.HTTPException:
                    log.warning(
                        "Could not send traceback to traceback channel use /tr"
                        "aceback to get the most recent error"
                    )
                    return
        else:
            log.exception(type(error).__name__, exc_info=error)


def setup(bot):
    bot.add_cog(Events(bot))
