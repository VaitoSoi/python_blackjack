from random import randint

import hikari

from lib.static import COLORS


def random_color():
    return hikari.Color.from_rgb(randint(0, 255), randint(0, 255), randint(0, 255))

def to_hikari_color(color: COLORS):
    return hikari.Color.from_hex_code(color.value)