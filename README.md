# Python Blackjack
A simple Blackjack bot written in Python with [Hikari](https://www.hikari-py.dev/), [Arc](https://arc.hypergonial.com/) and [Miru](https://miru.hypergonial.com/).

## I. Setup
To setup enviroment, install packages with this command:
```bash
uv sync
```

Then run this command follow its instruction:
```bash
python cli.py setup
```

For more options, run:
```bash
python cli.py setup --help
```

## II. Start the bot
After set up the environment, run this command:
```bash
python cli.py start
```

### III. Demo:

[!Matchs](https://cdn.discordapp.com/attachments/1489684297538338846/1489684345684889721/image.png?ex=69d15029&is=69cffea9&hm=bb65b44f36907d02efd7e7535e431fb5077180fb2c93f601fafdf0cd1f6a8a5c)

[!Guide](https://media.discordapp.net/attachments/1489684297538338846/1489684736757731418/image.png?ex=69d15086&is=69cfff06&hm=47c8bc748b75813555887b0f8762dc865653f828322c6be7ff0ce7bdb75c1cac&=&format=webp&quality=lossless)

[!History](https://media.discordapp.net/attachments/1489684297538338846/1489684837806768250/image.png?ex=69d1509e&is=69cfff1e&hm=dd0287583c41e1e9c47a918968ed86adcdc5c5636813465283c84a4705962038&=&format=webp&quality=lossless)

### IV. Environment:

| Name | Data type | Required | Note |
|------|-----------|----------|------|
|DB_URL| string    | ✅       |Must include async driver of the DB (eg. aiosqlite for SQLite) and Must be accepted by SQLAlchemy|
|TOKEN | string    | ✅       |      |

### V. Components

| Library | Purpose           | Note |
|---------|-------------------|------|
| Hikari  | Main bot          |      |
| Arc     | Command handler   |      |
| Miru    | Component handler |      |
| Click   | CLI               |      |
