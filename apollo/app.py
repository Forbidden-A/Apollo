import os
import traceback
from datetime import datetime
import asyncio
import aiofile
import json
from aiofile import AIOFile
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
        self.token = self._token

    def load_extensions(self):
        for extension in os.listdir('plugins'):
            try:
                self.load_extension(f'plugins.{extension[:-3]}') if extension.endswith('.py') else print(extension, 'is not a python file.')
            except lightbulb.errors.ExtensionMissingLoad:
                print(extension, 'is missing load function.')
            except lightbulb.errors.ExtensionError as e:
                print(extension, 'Failed to load.')
                print(' '.join(traceback.format_exception(type(e or e.__cause__), e or e.__cause__, e.__traceback__)))


def main():
    with open(r"../config.json", 'r') as fp:
        config = json.loads(fp.read())
    bot = Bot(prefix='a*', token=config.get('token'))
    bot.load_extensions()
    bot.run()


if __name__ == '__main__':
    exit(main())

