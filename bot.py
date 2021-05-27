import discord
from discord.ext import commands

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
    'cogs.server',
    'cogs.minecraft',
    'cogs.owner',
    'cogs.events',
    'cogs.fun',
    'cogs.news',
]


def get_prefix(bot, message):
    prefixes = [bot.config["prefix"]]
    return commands.when_mentioned_or(*prefixes)(bot, message)


description = """Hello! made by null"""


class ServerStatus(commands.Bot):
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

        # self.aiohttp = aiohttp.ClientSession(loop=self.loop)
        # asyncio.run(self.aiohttp.close())

        try:
            self.load_extension("jishaku")

        except Exception:
            log.info("jishaku is not installed, continuing...")

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

    async def on_ready(self):
        # self.database_commands = DatabaseCommands()

        log.info(f"Logged in as {self.user.name} - {self.user.id}")
        self.init_ok = True

    def run(self):
        log.info("Logging into Discord...")
        super().run(self.config["bot-token"])


if __name__ == "__main__":
    bot = ServerStatus()
    bot.help_command = PrettyHelp(ending_note=description)
    bot.run()
