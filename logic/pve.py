from datetime import datetime, timedelta
from typing import Callable, cast

import hikari
import miru

from lib.db import session_maker
from lib.static import COLORS, EMOJI, REPO_URL
from lib.util import to_hikari_color
from models.game import PvE as PvETable

from .base import EvaluationResult, MatchResult, SpecialResultWeight, card_evaluate


class PvE(miru.View):
    id: str
    user_id: str
    bot_deck: list[str]
    user_deck: list[str]
    cards: list[str]

    @staticmethod
    def get_result(bot: EvaluationResult, user: EvaluationResult) -> MatchResult:
        if bot == user:
            return "draw"

        # Try to parse str to int because data loaded from DB will always be str
        try:
            user = int(user)
        except (ValueError, TypeError): 
            pass
        try:
            bot = int(bot)
        except (ValueError, TypeError): 
            pass

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

    def __init__(
        self,
        id: str,
        user_id: str,
        bot_deck: list[str],
        user_deck: list[str],
        cards: list[str],
        *,
        timeout: float | int | timedelta | None = 120,
        autodefer: bool | miru.AutodeferOptions = True,
    ) -> None:
        super().__init__(timeout=timeout, autodefer=autodefer)
        self.id = id
        self.user_id = user_id
        self.bot_deck = bot_deck
        self.user_deck = user_deck
        self.cards = cards

    async def construct_embed(
        self, client: miru.Client | None = None, reveal: bool = False
    ) -> hikari.Embed:
        client = client or self.client
        me = await client.app.rest.fetch_my_user()
        embed = hikari.Embed()
        embed.color = to_hikari_color(COLORS.Blue)
        embed.set_author(
            name=f"{me.username} - Powered by Vaito",
            icon=me.make_avatar_url(),
            url=REPO_URL,
        )
        embed.set_footer("Blackjack Game")
        embed.timestamp = datetime.now().astimezone()
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

    async def construct_done_embed(
        self, result: MatchResult, client: miru.Client | None = None
    ) -> hikari.Embed:
        embed = await self.construct_embed(client, True)
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

    async def complete_game(self, client: miru.Client | None = None):
        user_evaluation = card_evaluate(self.user_deck)
        bot_evaluation = card_evaluate(self.bot_deck)

        condition_checker: Callable[[EvaluationResult], bool]
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

        result = PvE.get_result(bot_evaluation, user_evaluation)

        async with session_maker() as session:
            game = PvETable(
                id=self.id,
                user_id=self.user_id,
                user_evaluation=user_evaluation,
                user_deck=self.user_deck,
                bot_evaluation=bot_evaluation,
                bot_deck=self.bot_deck,
                winner=result,
            )
            session.add(game)
            await session.commit()

        return await self.construct_done_embed(result, client)

    @miru.button("Draw", emoji="👊", style=hikari.ButtonStyle.SECONDARY)
    async def draw(self, ctx: miru.ViewContext, button):
        self.user_deck.append(self.cards.pop())
        evaluation = card_evaluate(self.user_deck)
        if type(evaluation) is int or evaluation == "weak":
            embed = await self.construct_embed()
            await ctx.edit_response(embed=embed)
        else:
            embed = await self.complete_game()
            await ctx.edit_response(embed=embed, components=[])
            self.stop()

    @miru.button("Stop", emoji="🛑", style=hikari.ButtonStyle.DANGER)
    async def stop_(self, ctx, button):
        embed = await self.complete_game()
        await ctx.edit_response(embed=embed, components=[])
        self.stop()
