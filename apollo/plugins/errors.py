import lightbulb
from lightbulb import plugins


class Errors(plugins.Plugin):
    def __init__(self, bot: lightbulb.Bot):
        super().__init__()
        self.bot = bot

    @plugins.listener(event_type=lightbulb.errors.CommandErrorEvent)
    async def on_error(self, event: lightbulb.errors.CommandErrorEvent):
        error = event.error or event.error.__cause__

        if isinstance(error, lightbulb.errors.NotEnoughArguments):
            await event.message.reply("Insufficient arguments")
        elif isinstance(error, lightbulb.errors.CommandIsOnCooldown):
            await event.message.reply(
                f"Command on cooldown, retry in {error.retry_in:.2f}s"
            )
        else:
            raise error


def load(bot):
    bot.add_plugin(Errors(bot))
