"""
Miku Chatterbot Module
"""

from nextcord.ext import commands
import nextcord
from gtts import gTTS
import uuid
import os


class VoiceChat(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def join_vc(self, ctx):
        if ctx.voice_client:
            vc = ctx.voice_client
        else:
            vc = await ctx.author.voice.channel.connect()
        return vc

    @commands.command()
    async def join(self, ctx):
        await self.join_vc(ctx)

    @commands.command()
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send("I'm not connected to a voice channel")
        else:
            await ctx.voice_client.disconnect()
            await ctx.send("Bye.")

    @commands.command()
    async def tts(self, ctx, *, msg=None):
        if msg is None:
            await ctx.send("Give me something to say, baka!")
            return
        vc = await self.join_vc(ctx)
        tts = gTTS(msg)
        id = uuid.uuid4()
        temp_file = f"{id}.mp3"
        with open(temp_file, "wb") as f:
            tts.write_to_fp(f)
        vc.play(
            nextcord.FFmpegPCMAudio(source=temp_file),
            after=lambda e: os.remove(temp_file),
        )


def setup(client):
    client.add_cog(VoiceChat(client))
