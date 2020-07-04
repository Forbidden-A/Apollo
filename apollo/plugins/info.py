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
        embed = hikari.Embed(color=hikari.Colour.from_int(0x3498DB))
        embed.add_field(name="Hikari Version", value=hikari.__version__, inline=False)
        embed.add_field(name="Lightbulb Version", value=lightbulb.__version__, inline=False)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=False)
        embed.add_field(name="Uptime", value=text, inline=False)
        await context.reply(embed=embed)


def load(bot):
    bot.add_plugin(Info())
