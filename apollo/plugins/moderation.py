from datetime import timezone, datetime
from random import randint

import hikari
from PIL import Image
from lightbulb import plugins, commands, cooldowns, converters, checks, Bot
from lightbulb.context import Context


class Inspect(plugins.Plugin):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.date_format = "%a, %d, %b %Y"

    @staticmethod
    def display_time(seconds, granularity=2):
        result = []
        intervals = (
            ("years", 0x1E14320),
            ("months", 0x2819A0),
            ("weeks", 0x93A80),
            ("days", 0x15180),
            ("hours", 0xE10),
            ("minutes", 0x3C),
            ("seconds", 0x1),
        )

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip("s")
                result.append(f"{int(value)} {name}")
        return ", ".join(result[:granularity])

    # noinspection PyProtectedMember
    @cooldowns.cooldown(length=30, usages=3, bucket=cooldowns.UserBucket)
    @commands.group(aliases=["in"])
    async def inspect(self, context: Context):
        await self.bot._help_impl.send_group_help(
            context=context, group=context.command
        )

    @checks.guild_only()
    @cooldowns.cooldown(length=30, usages=3, bucket=cooldowns.UserBucket)
    @inspect.command(aliases=["m"])
    async def member(
        self, context: Context, member: converters.member_converter = None
    ):
        member: hikari.Member = member or context.member
        roles = await self.bot.rest.fetch_roles(context.guild_id)
        roles = sorted(
            [r for r in roles if r.id in member.role_ids],
            key=lambda r: r.position,
            reverse=True,
        )

        now = datetime.now(tz=timezone.utc)

        created_at = member.created_at.astimezone(timezone.utc)

        created_at = f"{created_at.strftime(self.date_format)}. {self.display_time((now - created_at).total_seconds())} ago"

        joined_at = member.joined_at.astimezone(timezone.utc)

        joined_at = f"{joined_at.strftime(self.date_format)}. {self.display_time((now - joined_at).total_seconds())} ago"

        embed = hikari.Embed(
            title="Inspect Member",
            description=f"**Name:** `{member.username}`\n"
            f"**Discriminator:** `{member.discriminator}`\n"
            f"**ID:** `{member.id}`\n"
            f"**Account Type:** `{'Bot' if member.is_bot else 'Human'}`\n"
            f"**Joined Discord:** `{created_at}`\n"
            f"**Joined here:** `{joined_at}`\n"
            f"**Display Name:** `{member.nickname or member.username}`\n"
            f"**Nickname:** `{member.nickname}`\n"
            f"**Rank:** <@&{roles[0].id}>\n"
            f"**• Colour:** `{str(roles[0].color).upper()}`\n",
            timestamp=now,
            colour=roles[0].color,
        )
        embed.add_field(
            inline=False,
            name=f"Roles [{len(roles)}]",
            value=", ".join(
                [
                    f"<@&{role.id}>" if "@everyone" != role.name else "@everyone"
                    for role in roles
                ]
            ),
        )
        embed.set_thumbnail(member.avatar)
        embed.set_footer(
            text=f"Requested by {context.member.nickname or context.member.username}",
            icon=str(context.member.avatar),
        )
        await context.reply(embed=embed)

    @cooldowns.cooldown(length=30, usages=3, bucket=cooldowns.UserBucket)
    @inspect.command(aliases=["u"])
    async def user(self, context: Context, user: converters.user_converter = None):
        user: hikari.User = user or context.author
        now = datetime.now(tz=timezone.utc)

        created_at = user.created_at.astimezone(timezone.utc)

        created_at = f"{created_at.strftime(self.date_format)}. {self.display_time((now - created_at).total_seconds())} ago"

        embed = hikari.Embed(
            title="Inspect User",
            colour=randint(0, 0xFFFFFF),
            description=f"**Name:** `{user.username}`\n"
            f"**Discriminator:** `{user.discriminator}`\n"
            f"**ID:** `{user.id}`\n"
            f"**Joined Discord:** `{created_at}`\n"
            f"**Account Type:** `{'Bot' if user.is_bot else 'Human'}`\n",
            timestamp=now,
        )
        embed.set_thumbnail(user.avatar)
        embed.set_footer(
            text=f"Requested by {context.author.username}", icon=context.author.avatar
        )
        await context.reply(embed=embed)

    @checks.guild_only()
    @cooldowns.cooldown(length=30, usages=3, bucket=cooldowns.UserBucket)
    @inspect.command(aliases=["g", "s", "server", "here"])
    async def guild(self, context: Context):
        guild: hikari.Guild = await self.bot.rest.fetch_guild(context.guild_id)
        guild.channels = await self.bot.rest.fetch_guild_channels(guild.id)
        guild.members = await self.bot.rest.fetch_members(guild.id)
        now = datetime.now(tz=timezone.utc)

        created_at = guild.created_at.astimezone(timezone.utc)

        created_at = f"{created_at.strftime(self.date_format)}. {self.display_time((now - created_at).total_seconds())} ago"

        owner = await self.bot.rest.fetch_user(guild.owner_id)
        embed = (
            hikari.Embed(
                title="Inspect Guild",
                colour=randint(0, 0xFFFFFF),
                timestamp=now,
                description=f"**Name:** `{guild.name}`\n"
                f"**ID:** `{guild.id}`\n"
                f"**Owner:** `{owner}`\n"
                f"**Members:** `{len(guild.members)}`\n"
                f"**• Humans:** `{len([member for member in guild.members if not member.is_bot])}`\n"
                f"**• Bots:** `{len([member for member in guild.members if member.is_bot])}`\n"
                f"**Roles:** `{len(guild.roles)}`\n"
                f"**Emojis:** `{len(guild.emojis)}`\n"
                f"**Created at:** `{created_at}`\n"
                f"**Channels:** `{len(guild.channels)}`\n"
                f"**• Categories:** `{len(list(filter(lambda channel: isinstance(channel, hikari.GuildCategory), guild.channels)))}`\n"
                f"**• Text:** `{len(list(filter(lambda channel: isinstance(channel, hikari.GuildTextChannel), guild.channels)))}`\n"
                f"**• Voice:** `{len(list(filter(lambda channel: isinstance(channel, hikari.GuildVoiceChannel), guild.channels)))}`\n"
                f"**Region:** `{guild.region}`\n"
                f"**AFK Channel:** {f'<#{guild.afk_channel_id}>' if guild.afk_channel_id else '`None`'}\n"
                f"**AFK Timeout:** `{guild.afk_timeout}`\n"
                f"**System Channel:** <#{guild.system_channel_id}>\n"
                f"**Is Large:** `{'Yes' if guild.is_large else 'No'}`\n"
                f"**MFA Enforced:** `{'Yes' if guild.mfa_level else 'No'}`\n"
                f"**Verification Level:** `{guild.verification_level}`",
            )
            .set_footer(
                text=f"Requested by {context.member.nickname or context.member.username}",
                icon=context.member.avatar,
            )
            .set_thumbnail(guild.icon_url)
        )
        await context.reply(embed=embed)

    @checks.guild_only()
    @cooldowns.cooldown(length=30, usages=3, bucket=cooldowns.UserBucket)
    @inspect.command(aliases=["c", "ch"])
    async def channel(self, context: Context, channel=None):
        now = datetime.now(tz=timezone.utc)
        add_topic = False
        channel = channel or context.channel_id
        try:
            if match := converters.CHANNEL_MENTION_REGEX.match(str(channel)):
                channel_id = match.group(1)
            else:
                channel_id = int(channel)
            channel: hikari.PartialChannel = await self.bot.rest.fetch_channel(
                channel_id
            )
        except (hikari.NotFound, ValueError):
            return await context.reply("Invalid channel")
        except hikari.Forbidden:
            return await context.reply("I don't have access to this channel..")
        created_at = channel.created_at.astimezone(timezone.utc)

        created_at = f"{created_at.strftime(self.date_format)}. {self.display_time((now - created_at).total_seconds())} ago"
        if isinstance(channel, hikari.GuildTextChannel):
            desc = (
                f"**Name:** `{channel.name}`\n"
                f"**ID:** `{channel.id}`\n"
                f"**Created at:** `{created_at}`\n"
                f"**Type:** `{channel.type.name}`\n"
                f"**Category:** {f'<#{channel.parent_id}>' if channel.parent_id else '`None`'}\n"
                f"**Position:** `{channel.position}`\n"
                f"**NSFW:** `{channel.is_nsfw}`\n"
                f"**Slowmode delay:** `{channel.rate_limit_per_user}`\n"
            )
            add_topic = True
        elif isinstance(channel, hikari.GuildVoiceChannel):
            desc = (
                f"**Name:** `{channel.name}`\n"
                f"**ID:** `{channel.id}`\n"
                f"**Created at:** `{created_at}`\n"
                f"**Type:** `{channel.type.name}`\n"
                f"**Category:** {f'<#{channel.parent_id}>' if channel.parent_id else '`None`'}\n"
                f"**Position:** `{channel.position}`\n"
                f"**NSFW:** `{channel.is_nsfw}`\n"
                f"**User limit:** `{channel.user_limit}`\n"
                f"**Bitrate:** `{channel.bitrate}`\n"
            )
        elif isinstance(channel, hikari.GuildCategory):
            desc = (
                f"**Name:** `{channel.name}`\n"
                f"**ID:** `{channel.id}`\n"
                f"**Created at:** `{created_at}`\n"
                f"**Type:** `{channel.type.name}`\n"
                f"**Position:** `{channel.position}`\n"
                f"**NSFW:** `{channel.is_nsfw}`\n"
            )
        else:
            desc = (
                f"**Name:** `{channel.name}`\n"
                f"**ID:** `{channel.id}`\n"
                f"**Created at:** `{created_at}`\n"
                f"**Type:** `{channel.type.name}`\n"
            )

        embed = hikari.Embed(
            title="Inspect Channel",
            colour=randint(0, 0xFFFFFF),
            timestamp=now,
            description=desc,
        )
        if add_topic:
            embed.add_field(name="Topic", value=channel.topic or "None")
        embed.set_footer(
            text=f"Requested by {context.member.nickname or context.member.username}",
            icon=context.author.avatar,
        )

        await context.reply(embed=embed)

    @checks.guild_only()
    @cooldowns.cooldown(length=30, usages=3, bucket=cooldowns.UserBucket)
    @inspect.command(aliases=["r"])
    async def role(self, context: Context, role: converters.role_converter = None):
        role: hikari.Role = role or (
            sorted(
                [
                    r
                    for r in await self.bot.rest.fetch_roles(context.guild_id)
                    if r.id in context.member.role_ids
                ],
                key=lambda r: r.position,
                reverse=True,
            )
        )[0]
        created_at = role.created_at.astimezone(timezone.utc)
        now = datetime.now(tz=timezone.utc)
        created_at = f"{created_at.strftime(self.date_format)}. {self.display_time((now - created_at).total_seconds())} ago"

        embed = hikari.Embed(
            title="Inspect Role",
            colour=role.colour,
            timestamp=now,
            description=f"**Name:** `{role.name}`\n"
            f"**ID:** `{role.id}`\n"
            f"**Colour:** `{str(role.colour).upper()}`\n"
            f"**Mention:** <@&{role.id}>\n"
            f"**Created at:** `{created_at}`\n"
            f"**Position:** `{role.position}`\n"
            f"**Is Managed:** `{'Yes' if role.is_managed else 'No'}`\n"
            f"**Is Mentionable:** `{'Yes' if role.is_mentionable else 'No'}`\n"
            f"**Is Hoisted:** `{'Yes' if role.is_hoisted else 'No'}`",
        )
        embed.set_footer(
            text=f"Requested by {context.member.nickname or context.member.username}",
            icon=context.member.avatar,
        )
        await context.reply(embed=embed)

    @checks.guild_only()
    @cooldowns.cooldown(length=30, usages=3, bucket=cooldowns.UserBucket)
    @inspect.command(aliases=["color", "co"])
    async def colour(self, context: Context, *, colour: str):
        c = str(randint(0x0, 0xFFFFFF)) if colour == "0" else colour
        try:
            if len(c.split(" ")) == 3:
                red, green, blue = [int(c) for c in c.split(" ")]
                colour: hikari.Colour = hikari.Colour.from_rgb(red, green, blue)
            elif len(c.split(" ")) == 1:
                colour: hikari.Colour = hikari.Colour.from_int(
                    int(c)
                ) if c.isdigit() else hikari.Colour.from_hex_code(c)
            else:
                await context.reply(
                    "Either enter 3 values representing rgb or 1 colour hex/decimal or 0 for a random colour"
                )
                return
        except ValueError:
            return await context.reply("Invalid colour.")
        Image.new(mode="RGB", size=(128, 128), color=colour.rgb).save("colour.webp")
        embed = (
            hikari.Embed(
                title="Inspect Colour",
                description=f"**Decimal:** `{int(colour)}`\n"
                f"**Hex:** `#{colour.raw_hex_code}`\n"
                f"**Rgb:** `{', '.join([str(v) for v in colour.rgb])}`",
                colour=colour,
                timestamp=datetime.now(timezone.utc),
            )
            .set_footer(
                text=f"Requested by {context.member.nickname or context.member.username if context.member else context.author.username}",
                icon=context.author.avatar,
            )
            .set_thumbnail(hikari.File("colour.webp"))
        )
        await context.reply(embed=embed)


def load(bot):
    bot.add_plugin(Inspect(bot))
