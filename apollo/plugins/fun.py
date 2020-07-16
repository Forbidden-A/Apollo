import html
import random
from datetime import datetime, timezone

import aiohttp
import hikari
from lightbulb import plugins, commands
from lightbulb.context import Context


class Fun(plugins.Plugin):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def echo(self, context: Context, *text):
        await context.message.delete()
        try:
            await context.message.reply(
                " ".join(text),
                mentions_everyone=False,
                user_mentions=False,
                role_mentions=False,
            )
        except (hikari.NotFound, hikari.Forbidden):
            pass

    @commands.command()
    async def meme(self, ctx):
        async with aiohttp.request(
            "get", "https://www.reddit.com/r/dankmemes/.json"
        ) as resp:
            json = await resp.json()
            children = json["data"]["children"]
            try:
                post = random.choice(children)
                data = post["data"]
                embed = hikari.Embed(
                    title=data["title"],
                    url=f"https://www.reddit.com{data['permalink']}",
                    colour=random.randint(0, 0xFFFFFF),
                )
                embed.set_image(
                    html.unescape(str(data["preview"]["images"][0]["source"]["url"]))
                )
                await ctx.reply(embed=embed)
            except (KeyError, IndexError):
                await ctx.reply("you")

    @commands.command()
    async def roll(self, context: Context, first: int = 1, last: int = 6):
        try:
            first, last = int(first), int(last)
        except ValueError:
            await context.reply(
                embed=hikari.Embed(
                    description=f"I choose {random.randint(1, 6)}",
                    colour=0x3498DB,
                    timestamp=datetime.now(tz=timezone.utc),
                ).set_footer(
                    icon=context.author.avatar, text="😀 btw ur numbers were bad"
                )
            )
            return
        await context.reply(
            embed=hikari.Embed(
                description=f"I choose {random.randint(first, last)}",
                colour=0x3498DB,
                timestamp=datetime.now(tz=timezone.utc),
            ).set_footer(icon=context.author.avatar, text="😀")
        )

    @commands.command()
    async def reverse(self, context: Context, *text):
        text = " ".join(text)
        text = text[::-1]
        await context.message.delete()
        await context.reply(text)


def load(bot):
    bot.add_plugin(Fun(bot))
