import dotenv
def get_env_var(key: str) -> str:
    dotenv_path = "../.env"
    dotenv.load_dotenv(dotenv_path)

    val = dotenv.get_key(dotenv_path, key)
    if val:
        return val
    else:
        val = input(f"{key} nenalezen. Zadejte jej prosím: ")
        print("\n")
        dotenv.set_key(dotenv_path, key, val)
        return val
def clear_env_var():
    dotenv_path = "../.env"
    dotenv.set_key(dotenv_path, "email", "")
    dotenv.set_key(dotenv_path, "heslo", "")