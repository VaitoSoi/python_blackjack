import re
from typing import Literal

CARD_REGEX = re.compile(r"^(\d|10|a|j|q|k)(?:h|d|c|s)$")

SpecialResult = Literal["weak", "bust", "pair", "blackjack", "charlie"]
MatchResult = Literal["bot", "user", "draw"]
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