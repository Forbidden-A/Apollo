import asyncio
import contextlib
import io
import platform
import re
import textwrap
import traceback
from datetime import datetime, timezone
import hikari
import lightbulb
from lightbulb import commands, plugins
from lightbulb.context import Context
from lightbulb.utils import pag, nav


class SuperUser(plugins.Plugin):
    def __init__(self, bot):
        super().__init__()
        self.last_result = -1
        self.bot = bot

    @staticmethod
    def get_syntax_error(error: SyntaxError) -> str:
        """return syntax error string from error"""
        if error.text is None:
            return f"{error.__class__.__name__}: {error}\n"
        return f'{error.text}{"^":>{error.offset}}\n{type(error).__name__}: {error}'

    async def execute_in_shell(self, context: Context, body):
        success = False
        start = datetime.now(tz=timezone.utc)
        pattern = re.compile(r"```(?P<syntax>.*)\n(?P<body>[^`]+?)```")
        if match := pattern.search(body):
            items = match.groupdict()
            body = items["body"]
        stack = contextlib.ExitStack()
        stream = io.StringIO()
        stack.enter_context(contextlib.redirect_stdout(stream))
        stack.enter_context(contextlib.redirect_stderr(stream))
        with stack:
            process = await asyncio.create_subprocess_shell(
                body, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            stream.write(stdout.decode())
            stream.write(stderr.decode())
        diff = datetime.now(tz=timezone.utc) - start
        success = process.returncode == 0
        stream.seek(0)
        lines = (
            "\n".join(stream.readlines())
            .replace(self.bot.token, "~TOKEN~")
            .replace("`", "´")
        )
        desc = (
            f"*** Python {platform.python_version()} - Hikari {hikari.__version__} - lightbulb {lightbulb.__version__}\n"
            f"{lines}"
            f"- Returned {process.returncode}"
        )
        paginator = pag.EmbedPaginator(max_lines=25, prefix="```diff", suffix="```")

        @paginator.embed_factory()
        def make_embed(index, content):
            return hikari.Embed(
                title=f"Executed in {diff.total_seconds() * 1000:.2f}ms",
                color=0x58EF92 if success else 0xE74C3C,
                description=f"`Page #{index + 1}` \nResult: {content}",
                timestamp=datetime.now(tz=timezone.utc),
            ).set_footer(
                text=f"Requested by {context.message.author.username}",
                icon=context.message.author.avatar,
            )

        for line in desc.splitlines():
            paginator.add_line(line)

        navigator = nav.EmbedNavigator(paginator.pages)
        await navigator.run(context=context)

    async def evaluate(self, context: Context, body):
        """
        Honestly I don't even know who made this method 😭 but I'm guessing its neko @nekoka#8788 correct me in discord?
        Update: According to dav neko made it
        """
        start = datetime.now(tz=timezone.utc)
        pattern = re.compile(r"```(?P<syntax>.*)\n(?P<body>[^`]+?)```")
        if match := pattern.search(body):
            items = match.groupdict()
            syntax = items["syntax"]
            body = items["body"]
        success = False
        body = "async def __invoke__(bot, context):\n" + textwrap.indent(body, " " * 4)
        stack = contextlib.ExitStack()
        stream = io.StringIO()
        stack.enter_context(contextlib.redirect_stdout(stream))
        stack.enter_context(contextlib.redirect_stderr(stream))

        with stack:
            try:
                env = {
                    "self": self,
                    "bot": context.bot,
                    "ctx": context,
                    "context": context,
                    "channel_id": context.channel_id,
                    "author": context.author,
                    "guild_id": context.guild_id,
                    "message": context.message,
                    "_": self.last_result,
                }
                env.update(globals())
                env.update(locals())
                exec(body, env)
                self.last_result = await env["__invoke__"](self.bot, context)
                stream.write(f"- Returned: {self.last_result!r}")
            except SyntaxError as ex:
                stream.write(self.get_syntax_error(ex))
            except Exception as ex:
                stream.write(
                    "".join(traceback.format_exception(type(ex), ex, ex.__traceback__))
                )
            else:
                success = True
        stream.seek(0)
        lines = (
            "\n".join(stream.readlines())
            .replace(self.bot.token, "~TOKEN~")
            .replace("`", "´")
        )
        desc = (
            f"*** Python {platform.python_version()} - Hikari {hikari.__version__} - lightbulb {lightbulb.__version__}\n"
            f"{lines}"
        )
        paginator = pag.EmbedPaginator(max_lines=25, prefix="```diff", suffix="```")

        @paginator.embed_factory()
        def make_embed(index, content):
            return hikari.Embed(
                title=f"Executed in {(datetime.now(tz=timezone.utc) - start).total_seconds() * 1000:.2f}ms",
                color=0x58EF92 if success else 0xE74C3C,
                description=f"`Page #{index + 1}` \nResult: {content}",
                timestamp=datetime.now(tz=timezone.utc),
            ).set_footer(
                text=f"Requested by {context.message.author.username}",
                icon=context.message.author.avatar,
            )

        for line in desc.splitlines():
            paginator.add_line(line)

        navigator = nav.EmbedNavigator(paginator.pages)
        await navigator.run(context=context)

    # noinspection PyUnusedLocal,PyProtectedMember
    @lightbulb.owner_only()
    @commands.command(aliases=["exec", "eval", "evaluate", "sh", "shell", "cmd"])
    async def execute(self, context: Context, *, body):
        sent = []

        async def new_send(*args, **kwargs):
            result = await self.bot.send(*args, **kwargs)
            sent.append(result) if result.channel_id == context.channel_id else ...
            return result

        self.bot.rest.create_message = new_send

        async def check(event):
            return event.message.id == context.message.id

        await self.execute_in_shell(
            context=context,
            body=context.message.content.lstrip(
                f"{context.prefix}{context.invoked_with}"
            ),
        ) if context.invoked_with in ("sh", "shell", "cmd") else await self.evaluate(
            context=context,
            body=context.message.content.lstrip(
                f"{context.prefix}{context.invoked_with}"
            ),
        )
        try:
            message_event = await context.bot.wait_for(
                hikari.events.MessageUpdateEvent, timeout=60.0, predicate=check
            )
            if message_event.message.content != context.message.content:
                new_message = await self.bot.rest.fetch_message(
                    message_event.message.channel_id, message_event.message.id,
                )
                command_context = Context(
                    self.bot,
                    new_message,
                    context.prefix,
                    context.invoked_with,
                    context.command,
                )
                command_args = self.bot.resolve_arguments(
                    message_event.message, context.prefix
                )[1:]
                for message in sent:
                    await message.delete()
                await self.bot._invoke_command(
                    context.command, command_context, command_args
                )
        except (hikari.Forbidden, hikari.NotFound):
            pass
        except asyncio.TimeoutError:
            pass
        self.bot.rest.create_message = self.bot.send


def load(bot):
    bot.add_plugin(SuperUser(bot))
