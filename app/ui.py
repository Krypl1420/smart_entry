import dotenv


def get_folder_dir() -> str:
    import tkinter as tk
    from tkinter import filedialog
    import time, sys

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    folder_path = filedialog.askdirectory(
        title="Vytvoř a vyber složku"
    )

    if folder_path == "":
        print("nebyla vybrána složka")
        time.sleep(3)
        sys.exit()

    return folder_path

def get_env_var(key: str) -> str:
    dotenv_path = "../.env"
    dotenv.load_dotenv(dotenv_path)

    val = dotenv.get_key(dotenv_path, key)
    if val:
        return val
    elif key.startswith("Cesta"):
        print(f"{key} nenalezen. Zadejte jej prosím: ")
        val = get_folder_dir()
    else:
        val = input(f"{key} nenalezen. Zadejte jej prosím: ").replace("\\","\\\\")
        print("\n")
    dotenv.set_key(dotenv_path, key, val)
    return val
def clear_env_var():
    dotenv_path = "../.env"
    dotenv.set_key(dotenv_path, "email", "")
    dotenv.set_key(dotenv_path, "heslo", "")



class Loading:
    def __init__(self, message:str = "Loading: "):
        self.loading_chars = "⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏".split(" ")
        self.index = 0
        self.message = message
    def update(self):
        print(f"{self.message}{self.loading_chars[self.index%len(self.loading_chars)]}", end="\r")
        self.index += 1
    def end(self, message = None):
        if message is None:
            message = self.message
        print(message)
    