# can't work yet lmao cuz still using old d.py

# stolen from https://github.com/ErrorNoInternet/disnake-paginator
# button design from pycord lol
# slightly modified

import disnake
import discord


async def dummy_response(interaction):
    await interaction.response.send_message(
        "You are not the sender of that command!", ephemeral=True
    )


class ChannelResponseWrapper:
    def __init__(self, channel):
        self.channel = channel
        self.sent_message = None

    async def defer(self, ephemeral=False):
        self.sent_message = await self.channel.send("I am thinking...")

    async def send_message(self, content=None, embed=None, view=None, ephemeral=False):
        self.sent_message = await self.channel.send(
            content=content, embed=embed, view=view
        )

    async def edit_message(self, content=None, embed=None, view=None):
        if content is None:
            content = self.sent_message.content
        if embed is None:
            if len(self.sent_message.embeds) > 0:
                embed = self.sent_message.embeds[0]
        await self.sent_message.edit(content=content, embed=embed, view=view)


class MessageInteractionWrapper:
    def __init__(self, ctx):
        self.name = "MessageInteractionWrapper"
        self.id = ctx.message.id
        self.author = ctx.message.author
        self.channel = ctx.message.channel
        self.created_at = ctx.message.created_at
        self.guild = ctx.message.guild
        self.response = ChannelResponseWrapper(ctx.message.channel)

    async def edit_original_message(self, content=None, embed=None, view=None):
        await self.response.edit_message(content=content, embed=embed, view=view)


def text_splitter(lines, chars=4096):
    size = 0
    message = []
    for line in lines:
        if len(line) + size > chars:
            yield message
            message = []
            size = 0
        message.append(line)
        size += len(line)
    yield message


class ButtonPaginator:
    def __init__(
        self,
        segments,
        title="",
        color=0x000000,
        prefix="",
        suffix="",
        target_page=1,
        timeout=300,
        button_style=disnake.ButtonStyle.gray,
        invalid_user_function=dummy_response,
    ):
        self.embeds = []
        self.current_page = target_page
        self.timeout = timeout
        self.button_style = button_style
        self.invalid_user_function = invalid_user_function

        for segment in segments:
            if isinstance(segment, discord.Embed):
                self.embeds.append(segment)
            else:
                self.embeds.append(
                    disnake.Embed(
                        title=title,
                        color=color,
                        description=prefix + segment + suffix,
                    ),
                )

        if self.current_page > len(segments) or self.current_page < 1:
            self.current_page = 1

        class PaginatorView(disnake.ui.View):
            def __init__(this, interaction):
                super().__init__()

                this.timeout = self.timeout
                this.interaction = interaction

            async def on_timeout(this):
                for button in this.children:
                    button.disabled = True
                await this.interaction.edit_original_message(
                    embed=self.embeds[self.current_page - 1], view=this
                )
                return await super().on_timeout()

            def update_page(this):
                for button in this.children:

                    if button.custom_id == "pagenum":
                        button.label = f"{self.current_page}/{len(self.embeds)}"

            @disnake.ui.button(
                label="<<",
                style=disnake.ButtonStyle.blurple,
                disabled=True if len(self.embeds) == 1 else False,
            )
            async def first_button(this, _, button_interaction):
                if button_interaction.author != this.interaction.author:
                    await self.invalid_user_function(button_interaction)
                    return

                if len(self.embeds) >= 15:
                    self.current_page = (self.current_page - 10) % len(self.embeds)
                    if self.current_page < 1:
                        self.current_page = len(self.embeds)
                    if self.current_page == 0:
                        self.current_page = 1
                else:
                    self.current_page = 1
                this.update_page()
                await button_interaction.response.edit_message(
                    embed=self.embeds[self.current_page - 1], view=this
                )

            @disnake.ui.button(
                label="<",
                style=disnake.ButtonStyle.red,
                disabled=True if len(self.embeds) == 1 else False,
            )
            async def previous_button(this, _, button_interaction):
                if button_interaction.author != this.interaction.author:
                    await self.invalid_user_function(button_interaction)
                    return

                self.current_page -= 1
                if self.current_page < 1:
                    self.current_page = len(self.embeds)
                this.update_page()
                await button_interaction.response.edit_message(
                    embed=self.embeds[self.current_page - 1], view=this
                )

            @disnake.ui.button(
                label=f"{self.current_page}/{len(self.embeds)}",
                style=disnake.ButtonStyle.gray,
                disabled=True,
                custom_id="pagenum",
            )
            async def page_button(*_):
                pass

            @disnake.ui.button(
                label=">",
                style=disnake.ButtonStyle.green,
                disabled=True if len(self.embeds) == 1 else False,
            )
            async def next_button(this, _, button_interaction):
                if button_interaction.author != this.interaction.author:
                    await self.invalid_user_function(button_interaction)
                    return

                self.current_page += 1
                if self.current_page > len(self.embeds):
                    self.current_page = 1
                this.update_page()
                await button_interaction.response.edit_message(
                    embed=self.embeds[self.current_page - 1], view=this
                )

            @disnake.ui.button(
                label=">>",
                style=disnake.ButtonStyle.blurple,
                disabled=True if len(self.embeds) == 1 else False,
            )
            async def last_button(this, _, button_interaction):
                if button_interaction.author != this.interaction.author:
                    await self.invalid_user_function(button_interaction)
                    return

                if len(self.embeds) >= 15:
                    self.current_page = (self.current_page + 10) % len(self.embeds)
                    if self.current_page > len(self.embeds):
                        self.current_page = 1
                    if self.current_page == 0:
                        self.current_page = len(self.embeds)
                else:
                    self.current_page = len(self.embeds)
                this.update_page()
                await button_interaction.response.edit_message(
                    embed=self.embeds[self.current_page - 1], view=this
                )

        self.view = PaginatorView

    async def send(self, ctx, ephemeral=False, deferred=False):
        interaction = MessageInteractionWrapper(ctx.channel.id)
        if not deferred:
            await interaction.response.send_message(
                embed=self.embeds[self.current_page - 1],
                view=self.view(interaction),
                ephemeral=ephemeral,
            )
        else:
            await interaction.edit_original_message(
                embed=self.embeds[self.current_page - 1], view=self.view(interaction)
            )
