# slurpybot.py

import asyncio
import importlib
import logging
import os

import discord
from discord.ext import commands

import webserver


logger = logging.getLogger(__name__)


def _read_channel_id(name):
    value = os.getenv(name)
    if not value:
        return None

    try:
        return int(value)
    except ValueError:
        logger.error("%s must be a numeric Discord channel ID.", name)
        return None


def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


GENERAL_ID = _read_channel_id("GENERAL_ID")
CHAI_ID = _read_channel_id("CHAI_ID")
FANTASY_ID = _read_channel_id("FANTASY_ID")
FANTASY_ENABLED = _env_flag("FANTASY_ENABLED", default=False)


# Feature imports are isolated so a broken optional integration cannot prevent
# the rest of Slurpy from reaching Discord.
play_blackjack = print_balance = daily_gift = show_leaderboard = None
try:
    from blackjack import play_blackjack, print_balance, daily_gift, show_leaderboard
except Exception:
    logger.exception("Blackjack integration is unavailable during startup.")

fort_news = fort_shop = fort_stats = fort_map = None
try:
    from fortnite import fort_news, fort_shop, fort_stats, fort_map
except Exception:
    logger.exception("Fortnite integration is unavailable during startup.")

send_weather = tell_joke = get_lebron = None
try:
    from others import send_weather, tell_joke, get_lebron
except Exception:
    logger.exception("Utility integrations are unavailable during startup.")

chai_chat = None
try:
    from chai import chai_chat
except Exception:
    logger.exception("Character chat integration is unavailable during startup.")

get_ai_response = None
try:
    from chat import get_ai_response
except Exception:
    logger.exception("OpenAI chat integration is unavailable during startup.")

main_menu = None
if not FANTASY_ENABLED:
    logger.info("Fantasy integration is disabled by FANTASY_ENABLED.")


async def _get_fantasy_main_menu():
    """Load Yahoo fantasy only when an enabled command actually needs it."""
    global main_menu
    if main_menu is not None:
        return main_menu

    try:
        fantasy_module = await asyncio.to_thread(importlib.import_module, "fantasy")
        main_menu = fantasy_module.main_menu
    except Exception:
        logger.exception(
            "Fantasy could not initialize. Slurpy will continue without it."
        )
        return None

    return main_menu

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
async def on_message(message):
    if message.author.bot:
        return

    await client.process_commands(message)

    if client.user not in message.mentions:
        return

    if message.channel.id != GENERAL_ID:
        await message.channel.send("Use me in general chat.")
        return

    if get_ai_response is None:
        await message.channel.send("my brain's offline rn, try me again in a bit")
        return

    content = message.content.replace(f"<@{client.user.id}>", "")
    content = content.replace(f"<@!{client.user.id}>", "")
    content = content.strip()

    if not content:
        content = "user just pinged the bot without a message"

    async with message.channel.typing():
        reply = await get_ai_response(
            user_id=str(message.author.id),
            username=message.author.display_name,
            message_text=content
        )

    await message.channel.send(reply)

@client.event
async def on_member_join(member):
    channel = client.get_channel(GENERAL_ID)
    if channel:
        await channel.send(f'**Welcome {member.name}!**\n\nTry **!commands** for available commands.')

@client.event
async def on_member_remove(member):
    channel = client.get_channel(GENERAL_ID)
    if channel:
        await channel.send(f'**Goodbye {member.name}... 🚬**')

@client.command()
async def commands(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
    else:

        message = (
                '**BASICS:**\n'
                '!hello, !abc, !commands\n\n'
                '**FORTNITE:**\n'
                '!fort, !shop, !stats <player name>, !map\n\n'
                '**GAMES:**\n'
                '!play, !bal, !gift, !scores\n\n'
                '**OTHERS:**\n'
                '!joke, !weather <city name>, !goat, !chat\n\n'

        )

        await ctx.send(message)

@client.command()
async def hello(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
    else:
        await ctx.send("Hello, I am your bot!")

@client.command()
async def abc(ctx):
    print("COMMAND RECIEVED")
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
    else:
        await ctx.send("123")

##################################################################################################################################################
#################################################################### FORTNITE ####################################################################
##################################################################################################################################################

@client.command()
async def fort(ctx):
    if fort_news is None:
        await ctx.send("fortnite's tweaking rn, try again in a bit")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await fort_news(ctx)

@client.command()
async def shop(ctx):
    if fort_shop is None:
        await ctx.send("fortnite's tweaking rn, try again in a bit")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await fort_shop(ctx)

@client.command()
async def map(ctx):
    if fort_map is None:
        await ctx.send("fortnite's tweaking rn, try again in a bit")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await fort_map(ctx)

@client.command()
async def stats(ctx, player_name: str):
    if fort_stats is None:
        await ctx.send("fortnite's tweaking rn, try again in a bit")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await fort_stats(ctx, player_name)

################################################################################################################################################
#################################################################### OTHERS ####################################################################
################################################################################################################################################

@client.command()
async def joke(ctx):
    if tell_joke is None:
        await ctx.send("the jokes are cooked rn, try again later")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await tell_joke(ctx)

@client.command()
async def weather(ctx, *, city: str):
    if send_weather is None:
        await ctx.send("weather's tweaking rn, try again in a bit")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await send_weather(ctx, city=city)

@client.command()
async def goat(ctx):
    if get_lebron is None:
        await ctx.send("lebron highlights are taking a timeout rn")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the general channel.")
        return
    await get_lebron(ctx)

@client.command()
async def chat(ctx):
    print("COMMAND RECIEVED")
    if chai_chat is None or CHAI_ID is None:
        await ctx.send("chai's tweaking rn, try again later")
        return
    if ctx.channel.id != CHAI_ID:
        await ctx.send('Use the **chai** channel for this command!')
        return
    await chai_chat(ctx)

@client.command()
async def fantasy(ctx):
    print("COMMAND RECIEVED")
    if not FANTASY_ENABLED:
        await ctx.send("fantasy's benched rn while yahoo sorts itself out")
        return
    if FANTASY_ID is None:
        await ctx.send("fantasy's missing its channel rn")
        return
    if ctx.channel.id != FANTASY_ID:
        await ctx.send('Use the **fantasy** channel for this command!')
        return
    fantasy_main_menu = await _get_fantasy_main_menu()
    if fantasy_main_menu is None:
        await ctx.send("fantasy's benched rn while yahoo sorts itself out")
        return
    await fantasy_main_menu(ctx)

################################################################################################################################################
#################################################################### GAMES #####################################################################
################################################################################################################################################

@client.command()
async def play(ctx):
    print("COMMAND RECIEVED")
    if play_blackjack is None:
        await ctx.send("blackjack's off the table rn, try again later")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await play_blackjack(ctx)

@client.command()
async def blackjack(ctx):
    print("COMMAND RECIEVED")
    if play_blackjack is None:
        await ctx.send("blackjack's off the table rn, try again later")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await play_blackjack(ctx)

@client.command()
async def gift(ctx):
    print("COMMAND RECIEVED")
    if daily_gift is None:
        await ctx.send("the aura bank's closed rn, try again later")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await daily_gift(ctx)

@client.command()
async def scores(ctx):
    print("COMMAND RECIEVED")
    if show_leaderboard is None:
        await ctx.send("the leaderboard's missing rn, try again later")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await show_leaderboard(ctx)

@client.command()
async def leaderboard(ctx):
    print("COMMAND RECIEVED")
    if show_leaderboard is None:
        await ctx.send("the leaderboard's missing rn, try again later")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await show_leaderboard(ctx)

@client.command()
async def balance(ctx):
    print("COMMAND RECIEVED")
    if print_balance is None:
        await ctx.send("the aura bank's closed rn, try again later")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await print_balance(ctx, ctx.author.id)

@client.command()
async def bal(ctx):
    print("COMMAND RECIEVED")
    if print_balance is None:
        await ctx.send("the aura bank's closed rn, try again later")
        return
    if ctx.channel.id != GENERAL_ID:
        await ctx.send(f"This command can only be used in the **general** channel.")
        return
    await print_balance(ctx, ctx.author.id)

def run_bot():
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    token = os.getenv("SLURPY_TOKEN")
    if not token:
        raise RuntimeError("SLURPY_TOKEN is required to start Slurpy.")
    if GENERAL_ID is None:
        raise RuntimeError("GENERAL_ID must be set to a numeric Discord channel ID.")

    logger.info("Starting Slurpy. Fantasy enabled: %s", FANTASY_ENABLED)
    webserver.keep_alive()
    client.run(token)


if __name__ == "__main__":
    run_bot()
