from os import getenv

from dotenv import load_dotenv

load_dotenv()

def require_env(var: str):
    val = getenv(var)
    if val is None:
        raise RuntimeError(f"{var} is required but not found")
    return val

TOKEN = require_env("TOKEN")
DB_URL = require_env("DB_URL")