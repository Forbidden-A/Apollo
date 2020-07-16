import logging
import os
import traceback
import typing
from datetime import datetime, timezone

import lightbulb
from hikari.impl.rest import client
from hikari.models import messages
from lightbulb.command_handler import BotWithHandler

client.RESTClientImpl = type("REST", (client.RESTClientImpl,), {})  # unslot


class Bot(lightbulb.Bot):
    def __init__(
        self,
        *,
        prefix: typing.Union[
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
        ],
        insensitive_commands: bool = False,
        **kwargs,
    ):
        super().__init__(
            prefix=prefix, insensitive_commands=insensitive_commands, **kwargs
        )
        self.start_time = datetime.now(tz=timezone.utc)
        self.token = self._token
        self.send = self.rest.create_message

    def load_extensions(self):
        for extension in os.listdir("plugins"):
            try:
                self.load_extension(f"plugins.{extension[:-3]}") if extension.endswith(
                    ".py"
                ) else print(extension, "is not a python file.")
            except lightbulb.errors.ExtensionMissingLoad:
                print(extension, "is missing load function.")
            except lightbulb.errors.ExtensionError as e:
                print(extension, "Failed to load.")
                print(
                    " ".join(
                        traceback.format_exception(
                            type(e or e.__cause__), e or e.__cause__, e.__traceback__
                        )
                    )
                )


def main():
    # Set path to bot directory
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    if token := os.getenv("APOLLO_TOKEN"):
        bot = Bot(prefix=["a*",], token=token, insensitive_commands=True)
        logging.getLogger("lightbulb").setLevel(logging.DEBUG)
        bot.load_extensions()
        bot.run()
    else:
        print(
            "Please set an environment variable called `APOLLO_TOKEN` and set its value as the bot's token."
        )


if __name__ == "__main__":
    exit(main())
