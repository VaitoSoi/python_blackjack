import json
from enum import Enum
from importlib.resources import as_file
from pathlib import Path
from random import choice
from typing import Final

cards: list[str] = []
numbers = ["a", "2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k"]
suits = ["h", "d", "c", "s"]
for number in numbers:
    for suit in suits:
        cards.append(number + suit)

CARDS: Final = cards

emojis: dict[str, str] = {}
emoji_json_path = Path("./static/emojis.json")
if emoji_json_path.exists():
    with as_file(emoji_json_path) as path:
        with open(path, "r") as file:
            data = json.load(file)
            for card in [*cards, "back"]:
                if card not in data:
                    raise ValueError(f"{card} emoji is missing")
                emojis[card] = data[card]
else:
    emojis = {card: card.upper() for card in CARDS} | {"back": "X"}

EMOJI: Final = emojis


class COLORS(Enum):
    Default = "#000000"
    Aqua = "#1ABC9C"
    DarkAqua = "#11806A"
    Green = "#57F287"
    DarkGreen = "#1F8B4C"
    Blue = "#3498DB"
    DarkBlue = "#206694"
    Purple = "#9B59B6"
    DarkPurple = "#71368A"
    LuminousVividPink = "#E91E63"
    DarkVividPink = "#AD1457"
    Gold = "#F1C40F"
    DarkGold = "#C27C0E"
    Orange = "#E67E22"
    DarkOrange = "#A84300"
    Red = "#ED4245"
    DarkRed = "#992D22"
    Grey = "#95A5A6"
    DarkGrey = "#979C9F"
    DarkerGrey = "#7F8C8D"
    LightGrey = "#BCC0C0"
    Navy = "#34495E"
    DarkNavy = "#2C3E50"
    Yellow = "#FFFF00"
    White = "#FFFFFF"
    Greyple = "#99AAb5"
    Black = "#23272A"
    DarkButNotBlack = "#2C2F33"
    NotQuiteBlack = "#23272A"
    Blurple = "#5865F2"
    Fuchsia = "#EB459E"

    @classmethod
    def random(cls):
        return choice(list(cls))


REPO_URL: Final = "https://git.vaito.dev/vaito/python_blackjack"
CARD_THUMBNAL_URL: Final = "https://git.vaito.dev/vaito/python_blackjack/raw/branch/main/assets/cards.jpg"