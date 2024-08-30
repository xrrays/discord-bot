# xoltairbot.py
# testing bot

import discord
from discord.ext import commands
from chai import chai_chat
from apikeys import XOLTAIR_TOKEN, GENERAL_ID, CHAI_ID, STATUS_ID
from blackjack import play_blackjack

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

client = commands.Bot(command_prefix='!', intents=intents)
class TestButtonView(discord.ui.View):
    @discord.ui.button(label="Click Me!", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Button clicked!")

@client.event
async def on_ready():
    print("BOT ONLINE")
    channel = client.get_channel(STATUS_ID)
    if channel:
        await channel.send(f'**BOT ONLINE**')

@client.command()
async def test(ctx):
    print("COMMAND RECIEVED")
    await ctx.send("button:", view=TestButtonView())

@client.command()
async def chat(ctx):
    print("COMMAND RECIEVED")
    channel = client.get_channel(CHAI_ID)
    if ctx.channel.id != channel.id:
        await ctx.send('Use the **chai** channel for this command!')
        return
    await chai_chat(ctx)

@client.command()
async def blackjack(ctx):
    print("COMMAND RECIEVED")
    channel = client.get_channel(CHAI_ID)
    if ctx.channel.id != channel.id:
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await play_blackjack(ctx)

client.run(XOLTAIR_TOKEN)