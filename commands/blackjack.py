import random
from uuid import uuid4

import arc
import miru
from miru.ext import nav as miru_nav
from sqlmodel import select

from lib.db import session_maker
from lib.static import CARDS
from logic.base import card_evaluate
from logic.guides import GuidePages
from logic.pve import PvE
from models.game import PvE as PvETable

plugin = arc.GatewayPlugin("blackjack")

base_group = plugin.include_slash_group("blackjack", "Start a Blackjack game")


async def history_autocomplete(data: arc.AutocompleteData[arc.GatewayClient, str]):
    async with session_maker() as session:
        stm = select(PvETable).where(PvETable.id.startswith(data.focused_value or ""))
        matchs = (await session.execute(stm)).scalars()

    return [match.id for match in matchs]


@base_group.include
@arc.slash_subcommand("history", "Get game history")
async def history(
    ctx: arc.GatewayContext,
    id: arc.Option[
        str,
        arc.StrParams(
            description="Get result of a match", autocomplete_with=history_autocomplete
        ),
    ],
    miru_client: miru.Client = arc.inject(),
) -> None:
    async with session_maker() as session:
        stm = select(PvETable).where(PvETable.id == id)
        match = (await session.execute(stm)).scalar()

    if match is None:
        await ctx.respond(f"Can't find match with ID `{id}`")
        return

    pve_view = PvE(
        id=match.id,
        user_id=match.user_id,
        bot_deck=match.bot_deck,
        user_deck=match.user_deck,
        cards=[],
    )
    result = PvE.get_result(match.bot_evaluation, match.user_evaluation)
    embed = await pve_view.construct_done_embed(result, miru_client)

    embed.add_field(
        "Match info:",
        f"**ID:** {id}\n**Played at:** <t:{round(match.created_at.timestamp())}:f>",
    )
    embed.set_footer(None)
    embed.timestamp = None

    await ctx.respond(embed=embed)
    return


@base_group.include
@arc.slash_subcommand("pve", "Start a Blackjack game with bot")
async def pve(ctx: arc.GatewayContext, miru_client: miru.Client = arc.inject()) -> None:
    match_id = uuid4().__str__()

    cards = random.sample(CARDS, len(CARDS))
    bot_deck = cards[:2]
    user_deck = cards[2:4]
    cards = cards[4:]

    pve_view = PvE(match_id, ctx.user.id.__str__(), bot_deck, user_deck, cards)

    bot_evaluation = card_evaluate(bot_deck)
    user_evaluation = card_evaluate(user_deck)

    if (type(bot_evaluation) is str and bot_evaluation != "weak") or (
        type(user_evaluation) is str and user_evaluation != "weak"
    ):
        embed = await pve_view.complete_game(miru_client)
        await ctx.respond(embed=embed)
        return

    embed = await pve_view.construct_embed(miru_client)
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
