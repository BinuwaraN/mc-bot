import logging
from datetime import datetime
from time import mktime
from typing import Dict, Text
from typing import Union
import aiohttp
import socket

import discord
import feedparser
import pytz
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext import tasks

Minecraft_News_RSS = "https://www.minecraft.net/en-us/feeds/community-content/rss"

log = logging.getLogger("bot")

class News(commands.Cog):
    def __init__(self, bot) -> None:
        """Init."""
        self.bot = bot
        self.last_media_data = datetime.now(pytz.utc)
        self.last_java_version_data = datetime.now(pytz.utc)

        self._resolver = aiohttp.AsyncResolver()
        self._connector = aiohttp.TCPConnector(
            resolver=self._resolver,
            family=socket.AF_INET,
        )
        self.ses = aiohttp.ClientSession(loop=bot.loop)
        self.mojang_service: Dict[str, str] = {}

        self.autopost.start()
        

    async def get_media(self) -> Union[discord.Embed, None]:
        """Get rss media."""
        # http_session = aiohttp.ClientSession()
        async with self.ses.get(Minecraft_News_RSS) as resp:
            text = await resp.text()
            

        data = feedparser.parse(text, "lxml")

        # select the most recent post
        latest_post = data["entries"][0]

        # run checks to see wether it should be posted

        time = datetime.fromtimestamp(mktime(latest_post["published_parsed"]), pytz.utc)

        # print(time)
        # print(self.last_media_data)

        if time <= self.last_media_data:
            return None

        async with self.ses.get(latest_post["id"]) as resp:
            text = await resp.text()

        soup = BeautifulSoup(text, "lxml")
        author_image = (
            f"https://www.minecraft.net"
            f"{soup.find('img', id='author-avatar').get('src')}"
        )
        author = soup.find("dl", class_="attribution__details").dd.string
        text = soup.find("div", class_="end-with-block").p.text

        embed = discord.Embed(
            title=soup.find("h1").string,
            description=text,
            # colour=self.bot.color,
            url=f"https://minecraft.net{latest_post['imageurl']}",
            thumbnail=author_image,
        )

        # add categories
        embed.set_image(url=f"https://minecraft.net{latest_post['imageurl']}")
        embed.set_thumbnail(url=author_image)
        embed.add_field(name=("Category"), value=latest_post["primarytag"])
        embed.add_field(name=("Author"), value=author)
        embed.add_field(
            name=("Publish Date"),
            value=" ".join(latest_post["published"].split(" ")[:4]),
        )

        # create footer
        embed.set_footer(text=("Article Published"))
        embed.timestamp = time
        self.last_media_data = time

        # create title
        embed.set_author(
            name=("New Article on Minecraft.net"),
            url=latest_post["id"],
            icon_url=(
                "https://www.minecraft.net/etc.clientlibs/minecraft"
                "/clientlibs/main/resources/img/menu/menu-buy--reversed.gif"
            ),
        )

        return embed

    async def get_java_releases(self) -> Union[discord.Embed, None]:
        async with self.ses.get(
            "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        ) as resp:
            data = await resp.json()

        last_release = data["versions"][0]

        format = "%Y-%m-%dT%H:%M:%S%z"
        time = datetime.strptime(last_release["time"], format)
        if time <= self.last_java_version_data:
            return None

        embed = discord.Embed(
            colour=self.bot.color,
        )

        embed.add_field(name=("Name"), value=last_release["id"])
        embed.add_field(
            name=("Package URL"),
            value=("[Package URL]({url})").format(url=last_release["url"]),
        )
        embed.add_field(
            name=("Minecraft Wiki"),
            value=(
                "[Minecraft Wiki](https://minecraft.fandom.com/Java_Edition_{id})"
            ).format(id=last_release["id"]),
        )

        embed.set_footer(text=("Article Published"))
        embed.timestamp = time
        self.last_java_version_data = time
        # create title
        embed.set_author(
            name=("New Minecraft Java Edition Snapshot"),
            url=f"https://minecraft.fandom.com/Java_Edition_{last_release['id']}",
            icon_url=(
                "https://www.minecraft.net/etc.clientlibs/minecraft"
                "/clientlibs/main/resources/img/menu/menu-buy--reversed.gif"
            ),
        )
        return embed
    
    @tasks.loop(minutes=10)
    async def autopost(self) -> None:
        await self.bot.wait_until_ready()
        channel = self.bot.get_channel(789243692887572535)

        release_embed = await self.get_java_releases()
        article_embed = await self.get_media()

        if article_embed is not None:
            log.info('New minecraft article')
            message = await channel.send(embed=article_embed)
        
        if release_embed is not None:
            log.info('New minecraft release')
            message = await channel.send(embed=release_embed)
        # await message.publish()

    def cog_unload(self) -> None:
        """Stop news posting tasks on cog unload."""
        self.autopost.cancel()

def setup(bot):
    bot.add_cog(News(bot))