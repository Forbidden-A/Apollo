import platform
from datetime import datetime as dt
import datetime

import lightbulb
import pytz
from lightbulb import plugins, commands
from lightbulb.context import Context
import hikari.events.guild


class Info(plugins.Plugin):
    def __init__(self):
        super().__init__()

    @commands.command()
    async def bot(self, context: Context):
        """Credits to Yoda#9999"""
        uptime = int(round((dt.now(tz=pytz.timezone('UTC')) - context.bot.start_time).total_seconds()))
        text = str(datetime.timedelta(seconds=uptime))

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
            timestamp=dt.now(tz=pytz.timezone('UTC'))
        )
        embed.add_field(name="Hikari Version", value=hikari.__version__, inline=False)
        embed.add_field(name="Lightbulb Version", value=lightbulb.__version__, inline=False)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=False)
        embed.add_field(name="Uptime", value=text, inline=False)
        await context.reply(embed=embed)


def load(bot):
    bot.add_plugin(Info())
