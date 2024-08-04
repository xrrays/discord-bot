import discord
from discord.ext import commands
import apikeys
import requests
import math
import random
from datetime import datetime
from jokeapi import Jokes
import fortnite_api

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

client = commands.Bot(command_prefix='!', intents=intents)

def chunk_message(message, chunk_size=2000):
    for i in range(0, len(message), chunk_size):
        yield message[i:i + chunk_size]

################################################################################################################################################
#################################################################### BASICS ####################################################################
################################################################################################################################################

@client.event
async def on_ready():
    print("BOT ONLINE")

@client.event
async def on_member_join(member):
    channel = client.get_channel(apikeys.GENERAL_ID)
    if channel:
        await channel.send(f'**Welcome {member.name}!**')

@client.event
async def on_member_remove(member):
    channel = client.get_channel(apikeys.GENERAL_ID)
    if channel:
        await channel.send(f'**Goodbye {member.name}... 🚬**')

@client.command()
async def commands(ctx):
    print("COMMAND RECIEVED")

    message = (
                '**BASICS:**\n'
                '!hello, !abc, !commands\n\n'
                '**FORTNITE:**\n'
                '!news, !shop, !stats <player name>, !map\n\n'
                '**OTHERS:**\n'
                '!joke, !weather <city name>\n\n'
    )

    await ctx.send(message)

@client.command()
async def hello(ctx):
    print("COMMAND RECIEVED")
    await ctx.send("Hello, I am your bot!")

@client.command()
async def abc(ctx):
    print("COMMAND RECIEVED")
    await ctx.send("123")

##################################################################################################################################################
#################################################################### FORTNITE ####################################################################
##################################################################################################################################################

fort_api = fortnite_api.FortniteAPI(api_key=apikeys.FORTNITE_API)

@client.command()
async def news(ctx):
    print("COMMAND RECIEVED")

    news_data = fort_api.news.fetch()
    br_news = news_data.br.motds
    news_date = news_data.br.date.strftime('%B %d, %Y') 

    news = []
    news.append(f'**{news_date}  🗞️**')
    for item in br_news:
        news_item = f"**{item.title}**\n{item.body}"
        news.append(news_item)

    await ctx.send("\n\n".join(news))

@client.command()
async def shop(ctx):
    print("COMMAND RECEIVED")

    shop_data = fort_api.shop.fetch()
    shop_date = shop_data.date.strftime('%B %d, %Y')
    daily_items = shop_data.daily.entries if shop_data.daily else []
    featured_items = shop_data.featured.entries if shop_data.featured else []

    categories = {}
    seen_skins = {}
    shop = []
    shop.append(f'**Shop Date:** {shop_date}  🛍️\n')


    # Check if skin is a duplicate/bundle, then add to seen skins dictionary with category, skin name and price
    def add_to_category(category_name, cosmetic_name, price):
        if cosmetic_name not in seen_skins or price < seen_skins[cosmetic_name]['price']:
            seen_skins[cosmetic_name] = {'price': price, 'category': category_name}
            # seen_skins = comestic_name: {price: price, category: category_name}

    for item in featured_items:
        category_name = item.layout.name
        for cosmetic in item.items:
            if cosmetic.type.value == 'outfit':
                add_to_category(category_name, cosmetic.name, item.final_price)
                
    for item in daily_items:
        category_name = 'Daily'
        for cosmetic in item.items:
            if cosmetic.type.value == 'outfit':
                add_to_category(category_name, cosmetic.name, item.final_price)

    # Check the category from seen skins and adds it to the categories dictionary
    for skin, data in seen_skins.items():
        if data['category'] not in categories:
            categories[data['category']] = []
        categories[data['category']].append(f"{skin} ({data['price']})")
        # Add the skin and price values from seen skins to the categories dictionary

    for category, items in categories.items():
        category_item = f'**{category}** - {", ".join(items)}\n'
        shop.append(category_item)

    message = '\n'.join(shop)
    for chunk in chunk_message(message):
        await ctx.send(chunk)

@client.command()
async def stats(ctx, player_name: str):
    print("COMMAND RECIEVED")

    try:
        stats_data = fort_api.stats.fetch_by_name(name=player_name)
        battle_pass = stats_data.battle_pass
        overall_stats = stats_data.stats.all.overall

        wins = math.floor(overall_stats.matches * (overall_stats.win_rate / 100))
        hours_played = math.floor(overall_stats.minutes_played / 60)

        stats_message = (
            f"**{player_name}'s Fortnite Stats  🔬**\n"
            f"Season Level: {battle_pass.level}\n"
            f"Matches Played: {overall_stats.matches}\n"
            f"Time Played: {hours_played} hours\n"
            f"Wins: {wins}\n"
            f"Win Rate: {overall_stats.win_rate:.3f}%\n"
            f"Kills: {overall_stats.kills}\n"
            f"Deaths: {overall_stats.deaths}\n"
            f"K/D: {overall_stats.kd}\n"
        )

        await ctx.send(stats_message)
    
    except fortnite_api.errors.Forbidden:
        await ctx.send(f"{player_name}'s stats are not public. 🐱")
    except fortnite_api.errors.NotFound:
        await ctx.send(f"{player_name}'s account does not exist.  👻")

@client.command()
async def map(ctx):
    print("COMMAND RECIEVED")

    map_data = fort_api.map.fetch()
    poi_image = map_data.poi_image
    today_date = datetime.now().strftime('%B %d, %Y')

    message = (f"**The Fortnite map on {today_date}:  📍**")
    await ctx.send(message)
    await ctx.send(poi_image)

################################################################################################################################################
#################################################################### OTHERS ####################################################################
################################################################################################################################################

@client.command()
async def joke(ctx):
    print("COMMAND RECIEVED")
    
    joke_api = await Jokes()
    joke = await joke_api.get_joke()
    if joke["type"] == "single":
        joke_text = joke["joke"]
    else:
        joke_text = f"**{joke['setup']}**\n*{joke['delivery']}*"

    await ctx.send(joke_text)

@client.command()
async def weather(ctx, *, city: str):
    print("COMMAND RECIEVED")
    
    weather_api = weather_api = f"http://api.weatherapi.com/v1/current.json?key={apikeys.WEATHER_API}&q={city}"

    response = requests.get(weather_api)
    data = response.json()

    city_name = data['location']['name']
    country = data['location']['country']
    local_time = data['location']['localtime']

    last_updated = data['current']['last_updated']
    temp_c = data['current']['temp_c']
    temp_f = data['current']['temp_f']
    wind_kph = data['current']['wind_kph']
    wind_mph = data['current']['wind_mph']
    precip_mm = data['current']['precip_mm']
    precip_in = data['current']['precip_in']
    condition = data['current']['condition']['text']
    humidity = data['current']['humidity']

    local_time_formatted = datetime.strptime(local_time, '%Y-%m-%d %H:%M').strftime('%B %d, %Y  |  %I:%M %p')
    last_updated_formatted = datetime.strptime(last_updated, '%Y-%m-%d %H:%M').strftime('%B %d, %Y  |  %I:%M %p')

    weather_info =  (f'**{city_name}, {country} 🗺️**\n'
                    f'**Local Timestamp:** {local_time_formatted} 🕒\n'
                    f'\n'
                    f'**Last Update:** {last_updated_formatted} 🕒\n'
                    f'**Temperature:** {temp_c}°C / {temp_f}°F 🌡️\n'
                    f'**Condition:** {condition} 🌥️\n'
                    f'**Wind:** {wind_kph} kph / {wind_mph} mph 💨\n'
                    f'**Precipitation:** {precip_mm} mm / {precip_in} in 💧\n'
                    f'**Humidity:** {humidity}% ☀️')
    
    await ctx.send(weather_info)

################################################################################################################################################
#################################################################### GAMES #####################################################################
################################################################################################################################################
#🃏
@client.command()
async def blackjack(ctx):
    print("COMMAND RECIEVED")



    



client.run(apikeys.BOT_TOKEN)