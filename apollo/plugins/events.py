from hikari import MessageCreateEvent
from lightbulb import plugins, Bot


class Events(plugins.Plugin):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @plugins.listener(MessageCreateEvent)
    async def on_message(self, event: MessageCreateEvent):
        if 292577213226811392 in event.message.user_mentions:
            await event.message.add_reaction("<:rooBeatDaPing:624358407440171030>")


def load(bot):
    bot.add_plugin(Events(bot))
