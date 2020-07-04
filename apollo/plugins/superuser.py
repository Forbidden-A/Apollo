import io
import os
import sys
import textwrap
import traceback
from datetime import datetime

import hikari
import pytz
from hikari.events import message
from lightbulb import commands, plugins
import lightbulb
from lightbulb.context import Context


class SuperUser(plugins.Plugin):
    def __init__(self):
        super().__init__()
        self.last_result = -1

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
            return f'```py\n{error.__class__.__name__}: {error}\n```'
        return f'```py\n{error.text}{"^":>{error.offset}}\n{type(error).__name__}: {error}```'

    # noinspection PyUnresolvedReferences
    async def execute(self, context: Context, body):
        """Credits to alot of people (multiple sources, R. Danny, nekokatt, ...) if I missed your name please send me a DM"""
        start = datetime.now()
        old_stdout = sys.stdout

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

        success = False
        env.update(globals())
        body = self.cleanup_code(body)
        stdout = buffer = io.StringIO()

        func = 'async def func():\n%s' % textwrap.indent(body, '  ')

        try:
            exec(f'{func}', env)
        except SyntaxError as e:
            lines = self.get_syntax_error(e).replace(context.bot.token, '~TOKEN~')
            embed = hikari.Embed(
                title=f"Executed in {(datetime.now() - start).total_seconds() * 1000:.2f}ms",
                color=hikari.colors.Color.from_int(0xE74C3C),
                description=f"""```md
                                # Python {sys.version}
                                {lines}
                                                ```""", timestamp=datetime.now(tz=pytz.timezone('UTC'))
            ).set_footer(text=f'Requested by {context.author.username}', icon=str(context.author.avatar.url))
            return await context.reply(embed=embed)
        func = env['func']
        output = ['\n', ]
        # noinspection PyBroadException
        try:
            sys.stdout = stdout
            ret = await func()
        except Exception:
            success = False
            value = stdout.getvalue()
            for line in f"{value}{traceback.format_exc()}".splitlines():
                output.append(line)
        else:
            success = True
            value = buffer.getvalue().replace(context.bot.token, '~TOKEN~')

            try:
                await context.message.add_reaction('\u2611')
            except (hikari.errors.NotFound, hikari.errors.Forbidden):
                pass
            if ret is None:
                success = True
                if value:
                    for line in value.splitlines():
                        output.append(line.replace(context.bot.token, '~TOKEN~'))
            else:
                self.last_result = ret
                for line in f"{value}{ret}".splitlines():
                    output.append(line.replace(context.bot.token, '~TOKEN~'))
        finally:
            sys.stdout = old_stdout
            buffer.close()
        output = '\n'.join(output)

        embed = hikari.Embed(
            title=f"Executed in {(datetime.now() - start).total_seconds() * 1000:.2f}ms",
            color=hikari.Colour.from_int(0x58EF92 if success else 0xE74C3C),
            description=(f"```md\n"
                         f"# Python {sys.version}"
                         f"{output}```"), timestamp=datetime.now(tz=pytz.timezone('UTC'))
        ).set_footer(text=f'Requested by {context.author.username}', icon=str(context.author.avatar.url))
        await context.reply(embed=embed)

    @lightbulb.owner_only()
    @commands.command(name='execute', aliases=['exec', 'ex', 'do'])
    async def execute_(self, context, *body):
        await self.execute(context=context, body=' '.join(body))

    # @lightbulb.owner_only()
    # @commands.command()
    # async def exec(self, context: Context, *body):
    #     if "import os" in body or "import sys" in body:
    #         return await context.reply("For security reasons you can't do that!")
    #     else:
    #
    #         body = ' '.join(body).strip('` ')
    #
    #         env = {'bot': context.bot, 'context': context, 'ctx': context, 'message': context.message,
    #                '_': self.last_result}
    #
    #         env.update(globals())
    #
    #         func = f"async def body():\n{textwrap.indent(body, ' ')}"
    #
    #         exec(func, env)
    #
    #         body = env['body']
    #
    #         # noinspection PyBroadException
    #         try:
    #             await body()
    #         except Exception:
    #             msg = await context.reply(f'```{traceback.format_exc()}```')
    #             await msg.add_reaction("\u274c")
    #
    #             def check(r):
    #                 return r.user_id == context.author.id and r.message_id == msg.id
    #
    #             reaction = await context.bot.wait_for(message.MessageReactionAddEvent, timeout=30.0, predicate=check)
    #
    #             if reaction.emoji.name == "❌":
    #                 await context.message.delete()
    #                 await msg.delete()


def load(bot):
    bot.add_plugin(SuperUser())
