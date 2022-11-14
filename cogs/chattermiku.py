"""
Miku Chatterbot Module
"""

import asyncio
import random
import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
import toolz
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from modules.chatterbot_stuff import ListTrainerWithTags
from modules.paginator import text_splitter
from replit import db



# when Paginator works again, we can uncomment this.
# from modules.paginator import ButtonPaginator, text_splitter


class Goodbye(Exception):
    "Raised when user has said goodbye to Miku"


class ChatterMiku(commands.Cog):
    def __init__(self, client):
        self.client = client
        if 'learning_mode' not in db:
            db['learning_mode'] = True
        learning_mode = db['learning_mode']
        self.chatbot = ChatBot(
            "MikuBot",
            logic_adapters=[
                "chatterbot.logic.MathematicalEvaluation",
                "chatterbot.logic.BestMatch",
            ],
            read_only=learning_mode
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
            choices={"on": "True", "off": "False"},
        )
    ):
        """Toggles MikuBot's learning mode.
    
        Parameters
        ----------
        inter: Interaction
            The interaction object    
        mode: str
            ON to let Miku learn from chats, OFF to disable learning.
        """
        mode_bool = mode == "True"
        if db['learning_mode'] == mode_bool:
          await inter.response.send_message(f"Miku learning mode is already `{mode_bool}` dummy!")          
        else:
          db['learning_mode'] = mode_bool
          self.chatbot = ChatBot(
              "MikuBot",
              logic_adapters=[
                  "chatterbot.logic.MathematicalEvaluation",
                  "chatterbot.logic.BestMatch",
              ],
              read_only=mode_bool
          )      
          await inter.response.send_message(f"Miku learning mode is now set to `{mode_bool}`")
      
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
        Statement = storage.get_model("statement")
        session = storage.Session()
        statements = session.query(Statement).filter()
        if s_filter is None:
            text_list = list(statements)
            # text_list_str = [f"- {x.text} ({x.conversation})" for x in statements]

        else:
            text_list = [x for x in statements if s_filter in x.text]
            # text_list_str = [
            #    f"- {x.text} ({x.conversation})" for x in statements if filter in x.text
            # ]
        print(f"{len(text_list)} found")
        text_list.sort(key=lambda x: x.text)
        text_list_str = toolz.unique(text_list, key=lambda x: x.text)
        text_list_str = "\n".join(
            [
                f"{idx+1}. {x.text} ({x.conversation})"
                for idx, x in enumerate(text_list_str)
            ]
        )
        text_list = [x.text for x in text_list]
        session.close()
        splitted_text = text_splitter(text_list_str)
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
                errors = 0
                for text in text_list:
                    try:
                        print(f'Deleting "{text}"')
                        self.chatbot.storage.remove(text)
                    except Exception as e:
                        print(f"Exception: {e}")
                        errors += 1
                await ctx.send(f"Done! {errors} errors")
            elif await_msg.content == "n":
                await ctx.send("Well ok then. I won't delete them.")
        except asyncio.TimeoutError:
            await ctx.send("Whoops. Times out!")


def setup(client):
    client.add_cog(ChatterMiku(client))    