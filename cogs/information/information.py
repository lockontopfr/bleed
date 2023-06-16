from random import choice
from time import time

from discord import Embed, Message
from discord.ext.commands import Cog, Command, Group, command

import config

from helpers.bleed import Bleed
from helpers.managers import Context


class Information(Cog):
    def __init__(self, bot: Bleed) -> None:
        self.bot: Bleed = bot

    @command(
        name="ping",
    )
    async def ping(self, ctx: Context) -> Message:
        """
        View the bot's latency
        """

        start = time()
        message = await ctx.send(content="..")
        finished = time() - start

        return await message.edit(
            content=f"it took `{int(self.bot.latency * 1000)}ms` to ping **{choice(config.ping_responses)}** (edit: `{finished:.2f}ms`)"
        )

    @command(
        name="help",
        usage="<command>",
        example="lastfm",
        aliases=["commands", "h"],
    )
    async def help(self, ctx: Context, *, command: str = None) -> Message:
        """
        View command information
        """

        if not command:
            return await ctx.send(
                f"{ctx.author.mention}: <https://bleed.bot/help>, join the discord server @ <https://bleed.bot/discord>"
            )

        command_obj: Command | Group = self.bot.get_command(command)
        if not command_obj:
            return await ctx.warn(f"Command `{command}` does not exist")

        embeds = list()
        for command in [command_obj] + (
            list(command_obj.walk_commands())
            if isinstance(command_obj, Group)
            else list()
        ):
            embed = Embed(
                color=config.Color.info,
                title=(
                    ("Group Command: " if isinstance(command, Group) else "Command: ")
                    + command.qualified_name
                ),
                description=command.help,
            )

            embed.add_field(
                name="Aliases",
                value=(", ".join(command.aliases) if command.aliases else "N/A"),
                inline=True,
            )
            embed.add_field(
                name="Parameters",
                value=(
                    ", ".join(command.clean_params) if command.clean_params else "N/A"
                ),
                inline=True,
            )

            information = command.information or {}
            if cooldown := command.cooldown:
                information["cooldown"] = f"{int(cooldown.per)} seconds"

            if command.qualified_name.startswith("antinuke"):
                information["permissions"] = "Server Owner"

            elif permissions := command.permissions:
                information["permissions"] = " & ".join(
                    [permission.replace("_", " ").title() for permission in permissions]
                )

            embed.add_field(
                name="Information",
                value=(
                    "\n".join(
                        [
                            getattr(config.Emoji, key) + " " + value
                            for key, value in information.items()
                        ]
                    )
                    if information
                    else "N/A"
                ),
                inline=True,
            )

            embed.add_field(
                name="Usage",
                value=(
                    f"```\nSyntax: {ctx.prefix}{command.qualified_name} {command.usage or ''}"
                    + f"\nExample: {ctx.prefix}{command.qualified_name} {command.example or ''}```"
                ),
                inline=False,
            )
            embed.set_footer(
                text=(
                    "Module: " + command.cog_name.lower() if command.cog_name else "N/A"
                ),
            )

            embeds.append(embed)

        await ctx.paginate(embeds)
