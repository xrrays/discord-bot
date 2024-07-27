import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print("the bot is online!")
    print("------------------")

@client.command()
async def hello(ctx):
    print("command recieved")
    await ctx.send("hello, i am your bot!")

client.run('MTI2Njc3NzQ5MzE0MzI4OTk5OA.Gkk86_.IVgrH3PC48TB6EYPfWzYjGB6RGY1juA-Z3TDIY')

