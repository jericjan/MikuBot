""" adpated from: https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot """


import os
import discord
from discord.ext import commands
import live

live.keep_alive()
discord.opus.load_opus("./opus/libopus.so.0.8.0")
client = commands.Bot(command_prefix="$", intents=discord.Intents.all())


@client.event
async def on_ready():
    print(f"{client.user} is awake.")


# load new cogs here
client.load_extension("cogs.loaders")
client.load_extension("cogs.CMD")
client.load_extension("cogs.chattermiku")
client.load_extension("cogs.vc")

try:
    client.run(os.getenv("TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
