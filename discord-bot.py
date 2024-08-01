import discord
from discord.ext import commands
from jokeapi import Jokes

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print("the bot is online!")

@client.event
async def on_member_join(member):

    joke_api = await Jokes()
    joke = await joke_api.get_joke()
    joke_text = joke['joke'] if joke['type'] == 'single' else f"{joke['setup']} - {joke['delivery']}"

    channel = client.get_channel(1266779124744327192)
    if channel:
        await channel.send(f'welcome {member.name} !')
        await channel.send(joke_text)

@client.event
async def on_member_remove(member):
    channel = client.get_channel(1266779124744327192)
    if channel:
        await channel.send(f'rest in piss {member.name}, we hated that dumbass')

@client.command()
async def hello(ctx):
    print("command recieved")
    await ctx.send("hello, i am your bot!")

@client.command()
async def abc(ctx):
    print("command recieved")
    await ctx.send("123")

@client.command()
async def joke(ctx):
    print("command receieved")
    
    joke_api = await Jokes()
    joke = await joke_api.get_joke()
    joke_text = joke['joke'] if joke['type'] == 'single' else f"{joke['setup']} - {joke['delivery']}"

    await ctx.send(joke_text)


client.run('MTI2Njc3NzQ5MzE0MzI4OTk5OA.Gkk86_.IVgrH3PC48TB6EYPfWzYjGB6RGY1juA-Z3TDIY')

