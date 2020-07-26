import base64
import re
import typing
from datetime import datetime, timezone
from io import BytesIO
from random import randint

import aiohttp
import hikari
from hikari import Bytes
from lightbulb import plugins, commands
from lightbulb.context import Context

PYTHON_3 = 24
NODEJS = 17
C_LANG = 6
CPP = 7
PHP = 8
PYTHON_2 = 5
RUBY = 12
GO_LANG = 20
SCALA = 21
BASH = 38
CSHARP = 1
HASKELL = 11
BRAINFUCK = 44
LUA = 14
KOTLIN = 43
JAVA = 4
R_LANG = 31
ENDPOINT = "http://rextester.com/rundotnet/api"
languages = {
    "r": R_LANG,
    "rlang": R_LANG,
    "kt": KOTLIN,
    "kotlin": KOTLIN,
    "lua": LUA,
    "py": PYTHON_3,
    "python": PYTHON_3,
    "js": NODEJS,
    "javascript": NODEJS,
    "c": C_LANG,
    "c++": CPP,
    "cpp": CPP,
    "py2": PYTHON_2,
    "go": GO_LANG,
    "scala": SCALA,
    "sc": SCALA,
    "bash": BASH,
    "hs": HASKELL,
    "haskell": HASKELL,
    "brainfuck": BRAINFUCK,
    "bf": BRAINFUCK,
    "java": JAVA,
    "php": PHP,
    "csharp": CSHARP,
    "cs": CSHARP,
}

CODE_BLOCK = re.compile(r"```(?P<syntax>.*)\n(?P<body>[^`]+?)```")


class ExecuteResponse:
    def __init__(
        self,
        warnings: typing.Optional[str],
        errors: typing.Optional[str],
        output: str,
        stats,
        files,
    ):
        self.output: typing.Optional[str] = output
        self.warnings: typing.Optional[str] = warnings
        self.errors: typing.Optional[str] = errors
        self.stats: str = stats
        self.files: typing.Optional[typing.List[str]] = files

    @property
    def discord_files(self) -> typing.List[Bytes]:
        if not self.files:
            return []

        def convert_file(b64, i):
            data = BytesIO()
            data.write(base64.b64decode(b64))
            data.seek(0)
            return Bytes(data, i)

        return [convert_file(b64, i) for i, b64 in enumerate(self.files)]

    @staticmethod
    def from_dict(response: dict):
        warnings = response["Warnings"]
        errors = response["Errors"]
        output = response["Result"]
        stats = response["Stats"]
        files = response["Files"]
        return ExecuteResponse(warnings, errors, output, stats, files)


class Run(plugins.Plugin):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def run(self, context: Context, block):
        if match := CODE_BLOCK.search(
            context.message.content.lstrip(f"{context.prefix}{context.invoked_with}")
        ):
            groups = match.groupdict()
            if not groups.get("syntax"):
                return await context.reply("you need to provide a valid language")
            elif not groups.get("body"):
                return await context.reply("invalid code block.")

            syntax, body = match.groups()
            if not syntax.lower() in languages.keys():
                return await context.reply("invalid language provided.")
            elif syntax.lower() in ("js", "javascript"):
                body = body.replace("console.log", "print")
            async with aiohttp.request(
                "get",
                ENDPOINT,
                data={
                    "Program": body,
                    "LanguageChoice": languages[syntax.lower()],
                    "Input": "",
                    "CompilerArgs": "",
                },
            ) as resp:
                run_response = ExecuteResponse.from_dict(await resp.json())
                output = run_response.output
                stats = run_response.stats
                warnings = run_response.warnings
                errors = run_response.errors
                files = run_response.discord_files
                embed = hikari.Embed(
                    description="Output:"
                    "```diff\n"
                    f"+ {output}\n\n"
                    f"+ {stats}```"
                    "Warnings:"
                    "```fix\n"
                    f"{warnings}\n"
                    "```"
                    "Errors:"
                    "```css\n"
                    f"[ {errors} ]\n"
                    "```",
                    timestamp=datetime.now(timezone.utc),
                    colour=randint(0x0, 0xFFFFFF),
                ).set_footer(
                    text=f"Requested by {context.message.author.username}",
                    icon=context.message.author.avatar,
                )
                await context.reply(embed=embed, attachments=files)
        else:
            return await context.reply("you need to provide a valid code block")


def load(bot):
    bot.add_plugin(Run(bot))
