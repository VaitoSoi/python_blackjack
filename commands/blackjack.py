import random
from uuid import uuid4

import arc
import miru
from miru.ext import nav as miru_nav

from lib.static import CARDS
from logic.guides import GuidePages
from logic.pve import PvE

plugin = arc.GatewayPlugin("blackjack")

base_group = plugin.include_slash_group("blackjack", "Start a Blackjack game")


@base_group.include
@arc.slash_subcommand("pve", "Start a Blackjack game with bot")
async def pve(ctx: arc.GatewayContext, miru_client: miru.Client = arc.inject()) -> None:
    match_id = uuid4().__str__()

    cards = random.sample(CARDS, len(CARDS))
    bot_deck = cards[:2]
    user_deck = cards[2:4]
    cards = cards[4:]

    pve_view = PvE(match_id, bot_deck, user_deck, cards)
    embed = await pve_view.contruct_embed(miru_client)
    await ctx.respond(embed=embed, components=pve_view)
    miru_client.start_view(pve_view)


@base_group.include
@arc.slash_subcommand("guide", "A basic guide to play Blackjack")
async def guide(ctx: arc.GatewayContext, miru_client: miru.Client = arc.inject()) -> None:
    navigator = miru_nav.NavigatorView(pages=GuidePages)
    builder = await navigator.build_response_async(miru_client)
    await ctx.respond_with_builder(builder)
    miru_client.start_view(navigator)



@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
