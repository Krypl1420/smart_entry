import os
from dotenv import load_dotenv, set_key

def get_env_var() -> str:
    dotenv_path = ".env"
    load_dotenv(dotenv_path)
    key = "DIS_TOKEN"

    val = os.getenv(key)
    if val:
        return val
    else:
        val = input("Discord Bot Token nenalezen. Zadejte jej prosím: ")
        set_key(dotenv_path, key, val)
        return val

print(get_env_var())