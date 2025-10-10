import discord

# Enable intent to read message content
intents = discord.Intents.default()
intents.message_content = True  

# Create the bot
client = discord.Client(intents=intents)

"""
+------------------+---------+---------+
| 2025-10-08 15:25 |  Horní  |  Dolní  |
+------------------+---------+---------+
| Smart entry zone | 6773.20 | 6771.40 |
|   Denní levely   | 6796.48 | 6753.52 |
|  Týdenní levely  | 6786.44 | 6693.56 |
+------------------+---------+---------+/
"""
@client.event
async def on_message(message):
    if message.author == client.user:  # ignore the bot's own messages
        return
    msg_list = message.content.split("|")
    smart_money = {
        "high" : float(msg_list[6].strip()),
        "low" : float(msg_list[7].strip())
    }
    return smart_money

# Paste your bot token here
client.run("YOUR_BOT_TOKEN")
 