import random
from nextcord.ext import commands
import nextcord


# client.run("TOKEN")


class CMD(commands.Cog):

    # def __init__(self, msg,command_prefix):
    # def __init__(self, msg):
    #    self.myMSG = msg
    def __init__(self, client):
        self.client = client
        self.memeArray = (
            "https://i.imgflip.com/6w0b3x.jpg",
            "https://i.imgflip.com/6w08xg.jpg",
            "https://i.imgflip.com/6w07fr.jpg",
        )

    @commands.command()
    async def speak(self, ctx, *, msg):
        await ctx.send("Aight so you said: " + msg)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        msg = message.content.lower()
        # I guess text eastereggs in here
        if "miku" in msg:
            await message.channel.send("omg that's me!")
        if "teto" in msg:
            await message.channel.send("tetotetotetotetotetotetoteto")
        if "mikudayo" in msg:
            await message.channel.send("Run.")
        if "help" in msg:
            await message.channel.send('Blink twice for "yes" thrice for "no"')

    def get_full_class_name(self, obj):
        module = obj.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return obj.__class__.__name__
        return module + "." + obj.__class__.__name__

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = nextcord.Embed(title=self.get_full_class_name(error), description=error)
        await ctx.send(embed=embed)
        raise error

    @commands.Cog.listener()
    async def on_application_command_error(self, inter, error):
        embed = nextcord.Embed(title=self.get_full_class_name(error), description=error)
        await inter.channel.send(embed=embed)
        raise error

    @commands.command()
    async def myCommand(self, ctx):
        await ctx.send("basic command template")

    @commands.command()
    async def pollo(self, ctx):
        await ctx.send("https://i.imgflip.com/6rf23s.jpg")

    @commands.command()
    async def meme(self, ctx):
        await ctx.send(random.choice(self.memeArray))

    @commands.command()
    async def deadchat(self, ctx):
        await ctx.send(":skull:")
        await ctx.send("Here I'd gather a random prompt")

    @commands.command()
    async def vtube(self, ctx):
        await ctx.send("My V-Tube Career boutta pop off")
        await ctx.send("https://www.youtube.com/shorts/syw2g1pKXjs")

    @commands.command()
    async def whois(self, ctx, *, msg=None):
        if msg == "miku":
            await ctx.send("Blue hair and tie. In your wifi")
        elif msg == "electron":
            await ctx.send("https://www.usa.gov/unemployment")
        elif msg == "teto":
            await ctx.send("upcoming virtual diva. ")
        else:
            await ctx.send("No idea. Who are **You**?")


def setup(client):
    client.add_cog(CMD(client))
