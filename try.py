loading_chars = "⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏".split(" ")

for i in range(20):
    print(loading_chars[i%10],"", end="")