from discord.ext.commands.core import Command, hooked_wrapped_callback

from helpers.managers import Context


class CommandCore(Command):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def invoke(self, ctx: Context, /) -> None:
        await self.prepare(ctx)

        if ctx.kwargs and (FlagConverter := getattr(ctx.command, "flags", None)):
            kwarg, argument = list(ctx.kwargs.keys())[-1], list(ctx.kwargs.values())[-1]
            if argument == None or isinstance(argument, (str)):
                argument = str(argument).replace("—", "")
                parsed = await FlagConverter.convert(ctx, argument)
                for name, value in parsed:
                    ctx.flags[name] = value
                    ctx.kwargs.update(
                        {
                            kwarg: (
                                str(ctx.kwargs.get(kwarg))
                                .replace("—", "--")
                                .replace(f"--{name} {value}", "")
                                .replace(f"--{name}", "")
                                .strip()
                            )
                            or (
                                ctx.command.params.get(kwarg).default
                                if isinstance(
                                    ctx.command.params.get(kwarg).default, str
                                )
                                else None
                            )
                        }
                    )

        ctx.invoked_subcommand = None
        ctx.subcommand_passed = None
        injected = hooked_wrapped_callback(self, ctx, self.callback)
        await injected(*ctx.args, **ctx.kwargs)


Command.invoke = CommandCore.invoke
