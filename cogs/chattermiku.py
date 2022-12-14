"""
Miku Chatterbot Module
"""

import asyncio
import random
import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from modules.chatterbot_stuff import ListTrainerWithTags
from modules import search_db
from replit import db


# when Paginator works again, we can uncomment this.
# from modules.paginator import ButtonPaginator, text_splitter


class Goodbye(Exception):
    "Raised when user has said goodbye to Miku"


class ChatterMiku(commands.Cog):
    def __init__(self, client):
        self.client = client
        if "read_only_mode" not in db:
            db["read_only_mode"] = True
        learning_mode = db["read_only_mode"]
        self.logic_adapters = [
            "chatterbot.logic.MathematicalEvaluation",
            "chatterbot.logic.BestMatch",
        ]
        self.chatbot = ChatBot(
            "MikuBot", logic_adapters=self.logic_adapters, read_only=learning_mode
        )
        self.trainer_w_tags = ListTrainerWithTags(self.chatbot)
        self.trainer = ListTrainer(
            self.chatbot
        )  # still need this cuz ListTrainerWithTags breaks with finding get_text_index_string() attribute and idk why

    @nextcord.slash_command(guild_ids=[1028350596065005598])
    async def learn(
        self,
        inter: nextcord.Interaction,
        mode: str = SlashOption(
            choices=['on','off'],
        ),
    ):
        """Toggles MikuBot's learning mode.

        Parameters
        ----------
        inter: Interaction
            The interaction object
        mode: str
            ON to let Miku learn from chats, OFF to disable learning.
        """
        modebool = mode == "off"
        if db["read_only_mode"] == modebool:
            await inter.response.send_message(
                f"Miku learning mode is already `{mode}` dummy!"
            )
        else:
            db["read_only_mode"] = modebool
            self.chatbot = ChatBot(
                "MikuBot", logic_adapters=self.logic_adapters, read_only=modebool
            )
            await inter.response.send_message(
                f"Miku learning mode is now set to `{mode}`"
            )

    @commands.command()
    async def sync(self, ctx):
        await self.client.sync_application_commands(guild_id=1028350596065005598)
        await ctx.send("Synced slash commands!")

    @commands.command()
    async def chat(self, ctx, *, msg=None):
        goodbyes = [
            "goodbye",
            "byebye",
            "cya",
            "see ya",
            "go away",
        ]  # temporary, might use chatterbot for this later but can't figure out rn

        async def get_response(msg):
            print("|----------")
            print(f'{ctx.author} told Miku "{msg}"')
            self.chatbot.read_only = db["read_only_mode"]
            print(f"Read-only = {self.chatbot.read_only}")
            bot_input = self.chatbot.get_response(msg)
            confidence = bot_input.confidence * 100
            print(f"{confidence:.2f}% confident")
            print(f"Response: {bot_input.text}")
            print(f"Convo type is: {bot_input.conversation}")
            print("----------|")
            if any(word in msg.lower() for word in goodbyes):
                raise Goodbye()
            await ctx.send(bot_input)

        if not msg:
            await ctx.send("Hey. You want to talk?")
        else:
            await get_response(msg)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        chatting = True
        while chatting:
            try:
                await_msg = await self.client.wait_for(
                    "message", check=check, timeout=60
                )
                await get_response(await_msg.content)

            except asyncio.TimeoutError:
                leave_msgs = [
                    "Oh... I have to go now. It's not like I enjoyed talking with you today. Hmph!",
                    "Why did you take so long to answer?? I'm leaving.",
                ]
                await ctx.send(random.choice(leave_msgs))
                chatting = False
            except Goodbye:
                gbye_msgs = [
                    "Oh, goodbye then. I won't miss you at all.",
                    "See ya, dummy!",
                ]
                await ctx.send(random.choice(gbye_msgs))
                chatting = False

    @commands.command()
    async def train(self, ctx, *, msg=None):

        if msg is None:
            await ctx.send("You've trained me nothing. Gimme something to train on, k?")
        else:
            msg = msg.strip("\n").split("\n")

            convo_type = [msg.pop(idx) for idx, x in enumerate(msg) if "convo=" in x]

            await ctx.send(f"Training on {len(msg)} lines...")

            if convo_type:
                convo_type = convo_type[0].split("=")[1]
                print(f"Training {msg} with convo type: {convo_type}")
                self.trainer_w_tags.train(msg, convo_type)
            else:
                print(f"Training {msg}")
                self.trainer.train(msg)

            await ctx.send("Done! Feel free to talk to me now with `$chat`")

    @commands.command()
    async def forget(self, ctx):
        await ctx.send("ight. m boutta forget everything i've learned")
        self.chatbot.storage.drop()

    @commands.command()
    async def random(self, ctx):
        random = self.chatbot.storage.get_random()
        await ctx.send(random)

    @commands.command()
    async def count(self, ctx):
        count = self.chatbot.storage.count()
        await ctx.send(f"There are {count} statements in my databse")

    async def do_search(self, ctx, storage, s_filter=None, title=None):
        "Searches through all bot responses stored in database"
        if title is None:
            title = "Searched through Miku's responses and found:"
        text_list, splitted_text = search_db.search(storage, s_filter)
        embed = nextcord.Embed()
        for index, message in enumerate(splitted_text):
            if index == 0:
                embed.title = title
            else:
                embed.title = ""
            embed.description = "".join(message)
            await ctx.send(embed=embed)
        return text_list

    @commands.command()
    async def search(self, ctx, *, s_filter):
        await self.do_search(ctx, self.chatbot.storage, s_filter)

    @commands.command()
    async def all(self, ctx):
        await self.do_search(ctx, self.chatbot.storage)

    @commands.command()
    async def delete(self, ctx, *, s_filter):
        text_list = await self.do_search(ctx, self.chatbot.storage, s_filter)
        await ctx.send(
            "Do you want to delete these? (y/n) (replaced with reactions soon)"
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            await_msg = await self.client.wait_for("message", check=check, timeout=60)
            if await_msg.content == "y":
                await ctx.send("Deleting...")
                errors = search_db.delete(self.chatbot.storage, text_list)
                await ctx.send(f"Done! {errors} errors")
            elif await_msg.content == "n":
                await ctx.send("Well ok then. I won't delete them.")
        except asyncio.TimeoutError:
            await ctx.send("Whoops. Times out!")


def setup(client):
    client.add_cog(ChatterMiku(client))
