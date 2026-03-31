from pathlib import Path

from arc import GatewayClient


def load_extension(client: GatewayClient, dir: Path):
    base_dir = Path().resolve()

    for entry in dir.iterdir():
        if not entry.is_file():
            continue

        if dir.is_absolute():
            relative_path = str(entry.relative_to(base_dir).resolve())
        else:
            relative_path = str(entry)
        relative_path = relative_path.replace("/", ".")
        relative_path = relative_path.replace(".py", "")

        client.load_extension(relative_path)