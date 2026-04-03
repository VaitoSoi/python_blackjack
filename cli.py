import json
import re
import sys

import click
import requests
from sqlalchemy.engine import make_url

BASE_DISCORD_API_URL = "https://discord.com/api/v10"


def info(text: str):
    return print(click.style("INFO", fg="white", bg="blue"), text)


def success(text: str):
    return print(
        click.style("SUCCESS", fg="white", bg="green"), click.style(text, fg="green")
    )


def warn(text: str):
    return print(
        click.style("WARN", fg="white", bg="yellow"), click.style(text, fg="yellow")
    )


def error(text: str):
    return print(click.style("ERROR", fg="white", bg="red"), click.style(text, fg="red"))


@click.group
def cli():
    pass


@cli.command
@click.option(
    "--offline",
    "-o",
    help="Skip data checking",
    flag_value=True,
    type=bool,
    default=False,
)
@click.option(
    "--skip-emoji",
    help="Skip emoji setup",
    flag_value=True,
    type=bool,
    default=False,
)
@click.option(
    "--just-template",
    help="Just create template for emoji JSON file",
    flag_value=True,
    type=bool,
    default=False,
)
def setup(offline: bool, skip_emoji: bool, just_template: bool):
    """Setup bot enviroment"""
    print("----- Setup env ------")
    if offline:
        warn("Bot token and DB url will not be checked.")

    token = click.prompt(click.style("Enter bot token", fg="blue"), type=str)

    # Token checker
    id: str | None = None
    username: str | None = None
    if not offline:
        res = requests.get(
            f"{BASE_DISCORD_API_URL}/users/@me", headers={"Authorization": f"Bot {token}"}
        )
        if res.status_code != 200:
            error("Can not verify bot token, is it a valid one?")
            sys.exit(1)

        data = res.json()
        id = data["id"]
        username = data["username"]
        info(f"Bot account is {username} ({id})")

    db_url = click.prompt(click.style("Enter DB url", fg="blue"), type=str)

    # DB url checker

    if not offline:
        try:
            url = make_url(db_url)
            if "sqlite" in url.drivername and url.host is None:
                warn(
                    "Dected SQLite in-memory database, which will be wiped every time you shutdown the bot."
                )

        except Exception:
            error("Can not verify DB url, is it a valid one or are the driver installed?")

    env_file = ""
    env_file += f"TOKEN={token}\n"
    env_file += f"DB_URL={db_url}"

    with open("./.env", "w") as file:
        file.write(env_file)

    print()
    success("Complete set up .env file")
    print(env_file)

    if skip_emoji:
        return

    print()
    print("----- Setup emojis -----")

    emojis: dict[str, str] = {}
    cards: list[tuple[str, str]] = []
    numbers = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["Heart", "Diamond", "Clover (Clubs)", "Spades (Pike)"]
    for number in numbers:
        for suit in suits:
            key = number.lower() + suit[0].lower()
            cards.append((f"{number} {suit}", key))
            emojis[key] = ""

    if not just_template:
        EMOJI_REGEX = re.compile(r"/(<a?)?:\w+:(\d{18}>)?/g")

        for card in cards:
            emoji = click.prompt(f"Emoji for {card[0]}", type=str)
            if EMOJI_REGEX.match(emoji) is None:
                error(f"{emoji} is not a valid emoji")
                sys.exit(1)
            emojis[card[1]] = emoji

    with open("./static/emojis.json", "w") as file:
        json.dump(emojis, file, indent=4)

    success("Created file static/emojis.json")

@cli.command
def start():
    """Start bot"""
    import main  # noqa: F401

if __name__ == "__main__":
    cli()
