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
            await context.message.reply(' '.join(text), mentions_everyone=False, user_mentions=False, role_mentions=False)
        except (hikari.NotFound, hikari.Forbidden):
            pass


def load(bot):
    bot.add_plugin(Fun(bot))
