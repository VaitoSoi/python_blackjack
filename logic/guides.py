import hikari
from miru.ext import nav

from lib.static import CARD_THUMBNAL_URL, COLORS, REPO_URL
from lib.util import to_hikari_color


def BaseEmbed():
    embed = hikari.Embed()
    embed.set_author(name="Blackjack Guide - Powered by Vaito", url=REPO_URL)
    embed.set_thumbnail(CARD_THUMBNAL_URL)
    embed.color = to_hikari_color(COLORS.Green)
    return embed


Disclaimer = BaseEmbed()
Disclaimer.title = "Disclaimer"
Disclaimer.description = """
+ This bot does not encourage gambling in any form.
+ The game provided by this bot is intended solely for entertainment purposes and are not intended for betting or gambling.
+ You must be at least 13 years old to use this bot!
+ You are solely responsible for all your actions.
+ The rules described here are a variant commonly played in southern Vietnam.
"""

BasicRule = BaseEmbed()
BasicRule.title = "Foundation - Basic rule"
BasicRule.description = """
At the start of the game, you will be dealt 2 cards.
Your goal is to draw additional cards so that the total value (total points) of the cards in your hand is **16 or higher** and **21 or lower**.
"""

Value = BaseEmbed()
Value.title = "Foundation - The value of each card"
Value.description = """
- The value of a card is equal to the number on the card (regardless of suit: spades, clubs, diamonds, hearts).
- Jacks (J), Queens (Q), and Kings (K) are worth 10.
- Aces (A) are worth 1, or 11, depending on the situation.

The value of a card, depending on the range, has its own specific name:
- < 16: Weak
- = 16: Hard hand
- >= 16 and <= 21: Valid range (legal value range)
- \\> 21 and <= 27: Bust
- \\> 27: Surrender
"""

WinLost = BaseEmbed()
WinLost.title = "Foundation - Determining the winner and loser"
WinLost.description = """
**You win when:**
- You have a valid hand value (16 ≤ hand value ≤ 21) AND
- Your hand value is higher than the dealer's (the house or possibly a bot) or the dealer has an invalid hand value.

**You tie when:**
- You have a valid hand value (16 ≤ hand value ≤ 21) AND
- The dealer has a valid hand value (16 ≤ hand value ≤ 21) AND
- Your hand value is equal to the dealer's hand value.

**You lose when:**
- You have an invalid value (value < 16 or 21 < value) OR
- Your value is lower than the dealer's (the dealer or possibly a bot).

**Note:** The cases above are only the basic scenarios; please refer to the special cases section for more details.
"""

SpecialCase = BaseEmbed()
SpecialCase.title = "Special Case"
SpecialCase.description = """
When you have the following cards in your hand, you will:
- Two Aces - Pair of Aces
- A J, Q, or K and an Ace - Blackjack
- Exactly 5 cards in your hand with a total value (point total) of 21 or less - Five-Card Charlie
- A total value greater than 27 - Surrender
"""

SpecialCase_WinLost = BaseEmbed()
SpecialCase_WinLost.title = "Special Case - Determining the winner and loser"
SpecialCase_WinLost.description = """
When either you or the dealer has a special hand (excluding “push”), the winner is determined in the following order:
**Blackjack > Natural 21 - Five Cards > Standard Hand**

Consider the following examples:
+ If the dealer has a natural 21 or five cards, you have a standard hand -> You lose
+ Dealer has Blackjack, you have a Pair or Five Cards -> You lose
+ Dealer has Blackjack, you have a standard hand -> You lose
+ Dealer has a normal hand, you have a normal hand -> Follow the basic rules
+ Dealer and you have the same hand (both blackjack, natural, etc.) -> Tie
The same applies to the opposite cases.

In the case of a **Surrender**, you will always lose unless the dealer busts or there is a Surrender.
"""

GuidePages = [
    nav.Page(embed=page)
    for page in [Disclaimer, BasicRule, Value, WinLost, SpecialCase, SpecialCase_WinLost]
]
Navigators = nav.NavigatorView(pages=GuidePages)
