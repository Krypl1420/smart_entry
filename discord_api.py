import discord

# Enable intent to read message content
intents = discord.Intents.default()
intents.message_content = True  

# Create the bot
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:  # ignore the bot's own messages
        return
    return message.channel, message.author, message.content

# Paste your bot token here
client.run("YOUR_BOT_TOKEN")
