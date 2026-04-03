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

### III. Environment:

| Name | Data type | Required | Note |
|------|-----------|----------|------|
|DB_URL| string    | ✅       |Must include async driver of the DB (eg. aiosqlite for SQLite) and Must be accepted by SQLAlchemy|
|TOKEN | string    | ✅       |      |

### IV. Components

| Library | Purpose           | Note |
|---------|-------------------|------|
| Hikari  | Main bot          |      |
| Arc     | Command handler   |      |
| Miru    | Component handler |      |
| Click   | CLI               |      |
