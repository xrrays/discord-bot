# slurpybot.py

import discord
from discord.ext import commands
from blackjack import play_blackjack, print_balance, daily_gift, show_leaderboard
from fortnite import fort_news, fort_shop, fort_stats, fort_map
from others import send_weather, tell_joke, get_lebron
from chai import chai_chat
import os
import webserver

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

client = commands.Bot(command_prefix='!', intents=intents)

################################################################################################################################################
#################################################################### BASICS ####################################################################
################################################################################################################################################

@client.event
async def on_ready():
    print("BOT ONLINE")

@client.event
async def on_member_join(member):
    channel = client.get_channel(int(os.getenv('GENERAL_ID')))
    if channel:
        await channel.send(f'**Welcome {member.name}!**\n\n\Try **!commands** for available commands.')

@client.event
async def on_member_remove(member):
    channel = client.get_channel(int(os.getenv('GENERAL_ID')))
    if channel:
        await channel.send(f'**Goodbye {member.name}... 🚬**')

@client.command()
async def help(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
    else:

        message = (
                '**BASICS:**\n'
                '!hello, !abc, !help\n\n'
                '**FORTNITE:**\n'
                '!news, !shop, !stats <player name>, !map\n\n'
                '**GAMES:**\n'
                '!play, !bal, !gift, !scores\n\n'
                '**OTHERS:**\n'
                '!joke, !weather <city name>, !goat, !chat\n\n'

        )

        await ctx.send(message)

@client.command()
async def hello(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
    else:
        await ctx.send("Hello, I am your bot!")

@client.command()
async def abc(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
    else:
        await ctx.send("123")

##################################################################################################################################################
#################################################################### FORTNITE ####################################################################
##################################################################################################################################################

@client.command()
async def fort(ctx):
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await fort_news(ctx)

@client.command()
async def shop(ctx):
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await fort_shop(ctx)

@client.command()
async def map(ctx):
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await fort_map(ctx)

@client.command()
async def stats(ctx, player_name: str):
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await fort_stats(ctx, player_name)

################################################################################################################################################
#################################################################### OTHERS ####################################################################
################################################################################################################################################

@client.command()
async def joke(ctx):
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await tell_joke(ctx)

@client.command()
async def weather(ctx, *, city: str):
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await send_weather(ctx, city=city)

@client.command()
async def goat(ctx):
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await get_lebron(ctx)

@client.command()
async def chat(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != int(os.getenv('CHAI_ID')):
        await ctx.send('Use the **chai** channel for this command!')
        return
    await chai_chat(ctx)

################################################################################################################################################
#################################################################### GAMES #####################################################################
################################################################################################################################################

@client.command()
async def play(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await play_blackjack(ctx)

@client.command()
async def gift(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await daily_gift(ctx)

@client.command()
async def scores(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await show_leaderboard(ctx)

@client.command()
async def bal(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != int(os.getenv('GENERAL_ID')):
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await print_balance(ctx, ctx.author.id)

webserver.keep_alive()
client.run(os.getenv('SLURPY_TOKEN'))
