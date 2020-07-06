import contextlib
import io
import platform
import re
import textwrap
import traceback
from datetime import datetime
import hikari
import lightbulb
from lightbulb import commands, plugins
from lightbulb.context import Context


class SuperUser(plugins.Plugin):
    def __init__(self, bot):
        super().__init__()
        self.last_result = -1
        self.bot = bot

    @staticmethod
    def cleanup_code(content: str) -> str:
        """get code from code blocks"""
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:(- 1)])
        return content.strip('` \n')

    @staticmethod
    def get_syntax_error(error: SyntaxError) -> str:
        """return syntax error string from error"""
        if error.text is None:
            return f'{error.__class__.__name__}: {error}\n'
        return f'{error.text}{"^":>{error.offset}}\n{type(error).__name__}: {error}'

    async def evaluate(self, context: Context, body):
        """
        Honestly I don't even know who made this method 😭 but I'm guessing its neko @nekoka#8788 correct me in discord?
        Update: According to dav neko made it
        """
        start = datetime.utcnow()
        match = re.search(r"```py(?:thon)?\n```", body)
        success = False
        if match:
            body = match.group(1)
        else:
            body = self.cleanup_code(body)
        body = "async def __invoke__(bot, context):\n" + textwrap.indent(body, " " * 4)
        stack = contextlib.ExitStack()
        stream = io.StringIO()
        stack.enter_context(contextlib.redirect_stdout(stream))
        stack.enter_context(contextlib.redirect_stderr(stream))

        with stack:
            try:
                env = {
                    'self': self,
                    'bot': context.bot,
                    'context': context,
                    'ctx': context,
                    'channel_id': context.channel_id,
                    'author': context.author,
                    'guild_id': context.guild_id,
                    'message': context.message,
                    '_': self.last_result,
                }
                env.update(globals())
                env.update(locals())
                exec(body, env)
                self.last_result = await env["__invoke__"](self.bot, context)
                stream.write(f"Returned: {self.last_result!r}")
            except SyntaxError as ex:
                stream.write(self.get_syntax_error(ex))
            except Exception as ex:
                stream.write("".join(traceback.format_exception(type(ex), ex, ex.__traceback__)))
            else:
                success = True
        stream.seek(0)
        lines = '\n'.join(stream.readlines()).replace(self.bot.token, '~TOKEN~').replace('`', '´')
        embed = hikari.Embed(
            title=f"Executed in {(datetime.utcnow() - start).total_seconds() * 1000:.2f}ms",
            color=hikari.Colour.from_int(0x58EF92 if success else 0xE74C3C),
            description=
            (f"Result:```md\n"
             f"# Python {platform.python_version()} - Hikari {hikari.__version__} - lightbulb {lightbulb.__version__}\n"
             f"{lines}```")
            , timestamp=datetime.utcnow()
        ).set_footer(text=f'Requested by {context.message.author.username}',
                     icon=str(context.message.author.avatar.url))
        await context.message.reply(embed=embed)

    @lightbulb.owner_only()
    @commands.command(name='execute', aliases=['exec', 'ex', 'do', 'eval', 'evaluate'])
    async def execute_(self, context, *body):
        await self.evaluate(context=context, body=' '.join(body))


def load(bot):
    bot.add_plugin(SuperUser(bot))
