from datetime import datetime

import lightbulb
import typing
import pytz
from hikari.models import messages
from lightbulb.command_handler import BotWithHandler


class Bot(lightbulb.Bot):
    def __init__(self, *, prefix: typing.Union[
        typing.Iterable[str],
        typing.Callable[
            [BotWithHandler, messages.Message],
            typing.Union[
                typing.Callable[
                    [BotWithHandler, messages.Message], typing.Iterable[str],
                ],
                typing.Coroutine[None, typing.Any, typing.Iterable[str]],
            ],
        ],
    ], **kwargs):
        super().__init__(prefix=prefix, **kwargs)
        self.start_time = datetime.now(tz=pytz.timezone('UTC'))
