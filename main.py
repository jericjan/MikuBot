""" adpated from: https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot """

import sys
import importlib
import os
import discord
from discord.ext import commands
import live


live.keep_alive()

client = commands.Bot(command_prefix="$", intents=discord.Intents.all())


@client.event
async def on_ready():
    print(f"{client.user} is awake.")


# load new cogs here
client.load_extension("CMD")
client.load_extension("chattermiku")


@client.command(aliases=["rl"])
async def reload(ctx, name):
    """reloads a cog. can also reload a python module."""
    try:
        client.reload_extension(name)
    except commands.ExtensionNotLoaded:
        try:
            importlib.reload(sys.modules[name])
        except KeyError:
            await ctx.send("failed to reload :(")
            return
    await ctx.send(f"{name} reloaded!")


@client.command(aliases=["l"])
async def load(ctx, name):
    client.load_extension(name)
    await ctx.send(f"{name} loaded!")


@client.command(aliases=["ul"])
async def unload(ctx, name):
    client.unload_extension(name)
    await ctx.send(f"{name} unloaded!")


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
