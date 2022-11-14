from nextcord.ext import commands
import importlib
import sys


class Loaders(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["rl"])
    async def reload(self, ctx, name):
        """reloads a cog. can also reload a python module."""
        try:
            self.client.reload_extension(f"cogs.{name}")
        except commands.ExtensionNotLoaded:
            try:
                importlib.reload(sys.modules[name])
            except KeyError:
                await ctx.send("failed to reload :(")
                return
        await ctx.send(f"{name} reloaded!")

    @commands.command(aliases=["l"])
    async def load(self, ctx, name):
        self.client.load_extension(f"cogs.{name}")
        await ctx.send(f"{name} loaded!")

    @commands.command(aliases=["ul"])
    async def unload(self, ctx, name):
        self.client.unload_extension(f"cogs.{name}")
        await ctx.send(f"{name} unloaded!")


def setup(client):
    client.add_cog(Loaders(client))
