""" adpated from: https://nextcordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot """


import os
import nextcord
from nextcord.ext import commands
from FlaskApp import flask

flask.keep_alive()
nextcord.opus.load_opus("./opus/libopus.so.0.8.0")
client = commands.Bot(command_prefix="$", intents=nextcord.Intents.all())


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
except nextcord.HTTPException as e:
    if e.status == 429:
        print("Goofy ahh Too Many Requests error")
        os.system("busybox reboot")
    else:
        raise e
