from pathlib import Path

import arc as arc_
import hikari
import miru as miru_

from lib.env import TOKEN
from lib.ext import load_extension

bot = hikari.GatewayBot(TOKEN)
arc = arc_.GatewayClient(bot)
miru = miru_.Client.from_arc(arc)

load_extension(arc, Path("./commands"))

bot.run()
