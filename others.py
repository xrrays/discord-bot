# others.py

from datetime import datetime
import logging
import requests
import os


logger = logging.getLogger(__name__)


async def send_weather(ctx, *, city: str):
    print("COMMAND RECIEVED")

    api_key = os.getenv('WEATHER_API')
    if not api_key:
        await ctx.send("weather's missing its api key rn")
        return

    weather_api = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"


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

async def tell_joke(ctx):
    print("COMMAND RECIEVED")

    try:
        from jokeapi import Jokes
    except Exception:
        logger.exception("Joke integration failed to import.")
        await ctx.send("the jokes are cooked rn, try again later")
        return

    joke_api = await Jokes()
    joke = await joke_api.get_joke(category=['Misc', 'Dark', 'Pun', 'Spooky', 'Christmas'])
    if joke["type"] == "single":
        joke_text = joke["joke"]
    else:
        joke_text = f"**{joke['setup']}**\n*{joke['delivery']}*"

    await ctx.send(joke_text)

async def get_lebron(ctx):
    api_key = os.getenv("GIPHY_KEY")
    if not api_key:
        await ctx.send("lebron highlights lost their api key rn")
        return

    link = f'https://api.giphy.com/v1/gifs/random?api_key={api_key}&tag=LeBron+James'
    response = requests.get(link)
    data = response.json()
    gif = data['data']['images']['original']['url']
    await ctx.send(gif)
