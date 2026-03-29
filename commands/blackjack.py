import random
import re
from datetime import datetime, timedelta
from typing import Callable, Literal, cast
from uuid import uuid4

import arc
import hikari
import miru

from lib.static import CARDS, COLORS, EMOJI, REPO_URL
from lib.util import random_color, to_hikari_color

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


CARD_REGEX = re.compile(r"^(\d|10|a|j|q|k)(?:h|d|c|s)$")

SpecialResult = Literal["weak", "bust", "pair", "blackjack", "charlie"]
EvalutionResult = int | SpecialResult


def card_evaluate(
    deck: list[str],
) -> EvalutionResult:
    """
    Response explaination
    | Name      | When                      |
    |-----------|---------------------------|
    | Weak      | Sum < 16                  |
    | Bust      | Sum > 21                  |
    | Pair      | Have a pair of ace        |
    | Blackjack | Have an Ace and a JQK     |
    | Charlie   | Have 5 cards and sum < 21 |
    | Number    | Normal case               |
    """

    jqk = 0
    ace = 0
    value = 0
    for card in deck:
        (number,) = CARD_REGEX.findall(card)
        if number == "a":  # Ace ~ 1 or 11
            value += 11
            ace += 1
        elif number in ["j", "q", "k"]:  # JQK ~ 10
            value += 10
            jqk += 1
        else:
            value += int(number)

    if len(deck) == 2:
        if ace == 2:
            return "pair"
        if jqk == 1 and ace == 1:
            return "blackjack"

    while value > 21 and ace > 0:  # Reduce Ace value
        ace -= 1
        value -= 10

    if value < 5 and len(deck) == 5:
        return "charlie"

    if value < 16:
        return "weak"

    if value > 21:
        return "bust"

    return value


SpecialResultWeight: dict[SpecialResult, int] = {
    "charlie": 3,
    "pair": 2,
    "blackjack": 1,
    "bust": -1,
    "weak": -2,
}
MatchResult = Literal["bot", "user", "draw"]


def get_result(bot: EvalutionResult, user: EvalutionResult) -> MatchResult:
    if bot == user:
        return "draw"

    if type(user) is str:
        # If user and bot both get special results: "pair", "blackjack", "charlie" or "weak", "bust"
        if type(bot) is str:
            user_weigth = SpecialResultWeight[user]
            bot_weigth = SpecialResultWeight[bot]

            if user_weigth < 0 and bot_weigth < 0:
                return "draw"

            elif user_weigth < bot_weigth:
                return "bot"
            else:
                return "user"

        # Only "pair", "blackjack", "charlie" left
        # And these results always beat the normal result
        return "user"

    # Bot get special results: "pair", "blackjack", "charlie" or "weak", "bust"
    if type(bot) is str:
        # These results always lose
        if bot in ["weak", "bust"]:
            return "user"

        # Remain results always wins
        return "bot"

    # Only left normal cases
    if cast(int, user) < cast(int, bot):
        return "bot"

    else:
        return "user"


class PvE(miru.View):
    id: str
    bot_deck: list[str]
    user_deck: list[str]
    cards: list[str]

    def __init__(
        self,
        id: str,
        bot_deck: list[str],
        user_deck: list[str],
        cards: list[str],
        *,
        timeout: float | int | timedelta | None = 120,
        autodefer: bool | miru.AutodeferOptions = True,
    ) -> None:
        super().__init__(timeout=timeout, autodefer=autodefer)
        self.id = id
        self.bot_deck = bot_deck
        self.user_deck = user_deck
        self.cards = cards

    async def contruct_embed(
        self, client: miru.Client | None = None, reveal: bool = False
    ) -> hikari.Embed:
        client = client or self.client
        me = await client.app.rest.fetch_my_user()
        embed = hikari.Embed()
        embed.color = random_color()
        embed.set_author(
            name=f"{me.username} - Powered by Vaito",
            icon=me.make_avatar_url(),
            url=REPO_URL,
        )
        embed.set_footer("Blackjack Game")
        embed.timestamp = datetime.now()
        embed.add_field(
            "Your deck",
            " ".join(EMOJI[card] for card in self.user_deck)
            + f" ({card_evaluate(self.user_deck)})",
        )
        if reveal:
            embed.add_field(
                "Bot deck",
                " ".join(EMOJI[card] for card in self.bot_deck)
                + f" ({card_evaluate(self.bot_deck)})",
            )
        else:
            embed.add_field("Bot deck", " ".join(EMOJI["back"] for _ in self.bot_deck))
        return embed

    async def contruct_done_embed(
        self, result: MatchResult, client: miru.Client | None = None
    ) -> hikari.Embed:
        embed = await self.contruct_embed(client, True)
        if result == "user":
            embed.color = to_hikari_color(COLORS.Green)
            embed.title = "🎉 You win 🎉"
        elif result == "bot":
            embed.color = to_hikari_color(COLORS.Red)
            embed.title = "🤖 Bot win 🎉"
        else:
            embed.color = to_hikari_color(COLORS.Yellow)
            embed.title = "🐧 Both win 🤖"
        return embed

    async def complete_game(self):
        user_evaluation = card_evaluate(self.user_deck)
        bot_evaluation = card_evaluate(self.bot_deck)

        condition_checker: Callable[[EvalutionResult], bool]
        if type(user_evaluation) is int:
            condition_checker = lambda evaluation: (  # noqa: E731
                (
                    type(evaluation) is not str
                    and cast(int, evaluation) < 21
                    and cast(int, evaluation) <= cast(int, user_evaluation)
                )
                or evaluation == "weak"
            )
        elif user_evaluation == "weak" or user_evaluation == "bust":
            condition_checker = lambda evaluation: (  # noqa: E731
                (
                    type(evaluation) is not str
                    and cast(int, evaluation) < 16
                    and cast(int, evaluation) < cast(int, user_evaluation)
                )
                or evaluation == "weak"
            )
        else:
            condition_checker = lambda _: False  # noqa: E731

        while condition_checker(bot_evaluation):
            self.bot_deck.append(self.cards.pop())
            bot_evaluation = card_evaluate(self.bot_deck)

        result = get_result(bot_evaluation, user_evaluation)
        return await self.contruct_done_embed(result)

    @miru.button("Draw", emoji="👊", style=hikari.ButtonStyle.SECONDARY)
    async def draw(self, ctx: miru.ViewContext, button):
        self.user_deck.append(self.cards.pop())
        evaluation = card_evaluate(self.user_deck)
        if type(evaluation) is int or evaluation == "weak":
            embed = await self.contruct_embed()
            await ctx.edit_response(embed=embed)
        else:
            embed = await self.complete_game()
            await ctx.edit_response(embed=embed, components=[])

    @miru.button("Stop", emoji="🛑", style=hikari.ButtonStyle.DANGER)
    async def stop_(self, ctx, button):
        embed = await self.complete_game()
        await ctx.edit_response(embed=embed, components=[])


@arc.loader
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
