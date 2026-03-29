import arc

plugin = arc.GatewayPlugin("ping")


@plugin.include
@arc.slash_command("ping", "Get bot latency")
async def ping(ctx: arc.GatewayContext):
    latency = ctx.client.app.heartbeat_latency

    if latency is None:
        await ctx.respond("Bot latency is currently unavailable.")
        return

    await ctx.respond(f"🏓 Pong `{latency * 1000:.2f}ms`")

@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
