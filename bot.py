from enum import IntEnum
from os import system
from typing import Optional
import aiohttp
import discord
from discord.ext import commands
from discord_slash import SlashCommand
import socket

import yaml
import logging
from pretty_help import PrettyHelp
from bot_errors import InvalidRefreshRate

discord.VoiceClient.warn_nacl = False  # don't need this warning

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

log = logging.getLogger('bot')
log.setLevel(logging.INFO)
log.addHandler(handler)

initial_extensions = [
    'cogs.events',
    'cogs.server',
    'cogs.minecraft',
    'cogs.owner',
    'cogs.fun',
    'cogs.news',
]


def get_prefix(bot, message):
    prefixes = [bot.config["prefix"]]
    return commands.when_mentioned_or(*prefixes)(bot, message)


description = """Hello! made by null"""


class MinecraftBot(commands.Bot):

    http_session: aiohttp.ClientSession
    _connector: aiohttp.TCPConnector
    _resolver: aiohttp.AsyncResolver

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            command_prefix=get_prefix,
            description=description,
            case_insensitive=True,
            activity=discord.Game("Starting up..."),
            intents=intents,
        )

        self.log = log

        log.info("Starting bot...")

        log.info("Loading config file...")
        self.config = self.load_config("config.yml")

        if self.config["refresh-rate"] < 30:
            raise InvalidRefreshRate(self.config["refresh-rate"])

        log.info("Loading extensions...")
        for extension in initial_extensions:
            self.load_extension(extension)

        log.info("Setting initial status before logging in...")
        status_cog = self.get_cog("Server")
        status, text = self.loop.run_until_complete(status_cog.get_status())
        game = discord.Game(text)
        status_cog.activity = game

        self._connection._status = status
        self.activity = game

        self.init_ok = None
        self.restart_signal = None

        self._last_exception = None
        self._shutdown_mode = ExitCodes.CRITICAL
        self.uptime = None

    async def pre_flight(self) -> None:

        self._resolver = aiohttp.AsyncResolver()
        # Use AF_INET as its socket family to prevent HTTPS related
        # problems both locally and in production.
        self._connector = aiohttp.TCPConnector(
            resolver=self._resolver,
            family=socket.AF_INET,
        )

        # Client.login() will call HTTPClient.static_login()
        # which will create a session using this connector attribute.
        self.http_session = aiohttp.ClientSession()

        # Load important cogs
        # self.add_cog(Events(self))

    async def start(self, *args, **kwargs):
        """
        Overridden start which ensures cog load and other
        pre-connection tasks are handled
        """
        await self.pre_flight()
        return await super().start(*args, **kwargs)

    def load_config(self, filename):
        with open(filename, "r") as f:
            return yaml.safe_load(f)

    async def on_command(self, ctx):
        destination = None

        if ctx.guild is None:
            destination = "Private Message"
        else:
            destination = f"#{ctx.channel} ({ctx.guild})"

        log.info(f"{ctx.author} in {destination}: {ctx.message.content}")

    async def send_unexpected_error(self, ctx, error):
        if hasattr(error, 'original'):
            return
        em = discord.Embed(
            title=":warning: Unexpected Error",
            color=discord.Color.gold(),
        )

        description = (
            "An unexpected error has occured"
            f"```py\n{error}```\n"
        )

        em.description = description
        await ctx.send(embed=em)

    async def shutdown(self, *, restart: Optional[bool] = False) -> None:
        """Gracefully quit bot.

        The program will exit with code :code:`0` by default.

        Parameters
        ----------
        restart : bool
            If :code:`True`, the program will exit with code :code:`26`. If the
            launcher sees this, it will attempt to restart the bot.

        """
        if not restart:
            self._shutdown_mode = ExitCodes.SHUTDOWN
        else:
            self._shutdown_mode = ExitCodes.RESTART

        await self.close()
        await self.http_session.close()
        system.exit(self._shutdown_mode)

    async def on_ready(self):
        # self.database_commands = DatabaseCommands()

        log.info(f"Logged in as {self.user.name} - {self.user.id}")
        self.init_ok = True

    def run(self):
        log.info("Logging into Discord...")
        super().run(self.config["bot-token"])


class ExitCodes(IntEnum):
    # This needs to be an int enum to be used
    # with sys.exit
    CRITICAL = 1
    SHUTDOWN = 0
    RESTART = 26


if __name__ == "__main__":
    bot = MinecraftBot()
    slash = SlashCommand(bot, sync_commands=True, sync_on_cog_reload=True)

    bot.help_command = PrettyHelp(ending_note=description)

    bot.run()
