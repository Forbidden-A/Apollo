import platform
from datetime import datetime, timezone
import aiohttp
import hikari.events.guild
import lightbulb
from lightbulb import plugins, commands
from lightbulb.context import Context


class Info(plugins.Plugin):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @staticmethod
    def display_time(seconds, granularity=2):
        result = []
        intervals = (
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),  # 60 * 60 * 24
            ('hours', 3600),  # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append(f"{int(value)} {name}")
        return ', '.join(result[:granularity])

    @commands.group()
    async def info(self, context: Context):
        return

    @info.command()
    async def bot(self, context: Context):
        """Credits to Yoda#9999"""
        diff = datetime.utcnow() - self.bot.start_time
        uptime = self.display_time(diff.total_seconds())

        embed = hikari.Embed(
            color=hikari.Colour.from_int(0x3498DB),
            description=(
                "Apollo is a discord bot made using [Hikari](https://nekokatt.gitlab.io/hikari/) and [Lightbulb](https://tandemdude.gitlab.io/lightbulb/)\n"
                "[Hikari Discord](https://discord.com/invite/Jx4cNGG)\n"
                "[Hikari Docs](https://nekokatt.gitlab.io/hikari/hikari/index.html)\n"
                "[Hikari Gitlab](https://gitlab.com/nekokatt/hikari)\n"
                "[Hikari PyPi](https://pypi.org/project/hikari/)\n"
                "[Lightbulb](https://tandemdude.gitlab.io/lightbulb/)\n"
                "[Lightbulb Docs](https://tandemdude.gitlab.io/lightbulb/)\n"
                "[Apollo](https://gitlab.com/Forbidden-A/apollo)"
            ),
            timestamp=datetime.now(tz=timezone.utc)
        )
        embed.add_field(name="Hikari Version", value=hikari.__version__, inline=False)
        embed.add_field(name='Aiohttp Version', value=aiohttp.__version__, inline=False)
        embed.add_field(name="Lightbulb Version", value=lightbulb.__version__, inline=False)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=False)
        embed.add_field(name="Uptime", value=uptime, inline=False)
        await context.reply(embed=embed)


def load(bot):
    bot.add_plugin(Info(bot))
