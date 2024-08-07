# xoltairbot.py

import discord
from discord.ext import commands
from fortnite import fort_shop
from others import get_lebron
from apikeys import XOLTAIR_TOKEN, GENERAL_ID, GIPHY_KEY
import requests

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print("BOT ONLINE")
    channel = client.get_channel(GENERAL_ID)
    if channel:
        await channel.send(f'**BOT ONLINE**')

@client.command()
async def test(ctx):
    print("COMMAND RECIEVED")
    await ctx.send("Hello, I am your bot!")

@client.command()
async def testshop(ctx):
    if ctx.channel.id != int(GENERAL_ID):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await fort_shop(ctx)

@client.command()
async def testlebron(ctx):
        if ctx.channel.id != int(GENERAL_ID):
            await ctx.send(f"This command can only be used in the general channel.")
            return
        await get_lebron(ctx)

client.run(XOLTAIR_TOKEN)