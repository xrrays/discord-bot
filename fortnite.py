# fortnite.py

import math
from datetime import datetime
import fortnite_api
import os, aiohttp
from apikeys import FORTNITE_API as FORTNITE_API_LOCAL

fort_api = fortnite_api.FortniteAPI(api_key=os.getenv('FORTNITE_API'))
API_KEY = os.getenv("FORTNITE_API") or FORTNITE_API_LOCAL

def chunk_message(message, chunk_size=2000):
    for i in range(0, len(message), chunk_size):
        yield message[i:i + chunk_size]

async def fort_news(ctx):
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

async def fort_shop(ctx):
    print("COMMAND RECEIVED")
    import aiohttp, os
    from datetime import datetime

    API_KEY = os.getenv("FORTNITE_API") or FORTNITE_API_LOCAL
    if not API_KEY:
        return await ctx.send("missing FORTNITE_API key (env or apikeys.py).")

    url = "https://fortnite-api.com/v2/shop"
    headers = {"Authorization": str(API_KEY)}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return await ctx.send(f"Shop error: HTTP {resp.status}")
            payload = await resp.json()

    data = payload.get("data", {})
    entries = data.get("entries", []) or []
    if not entries:
        return await ctx.send("⚠️ Shop returned no entries today.")

    shop_date = datetime.fromisoformat(data["date"].replace("Z", "+00:00")).strftime("%B %d, %Y")

    # collect section/category names
    categories = set()
    for entry in entries:
        cat = (
            ((entry.get("layout") or {}).get("name"))
            or ((entry.get("section") or {}).get("name"))
            or "Unknown"
        )
        categories.add(cat)

    # build simple output: just the category names
    lines = [f'**Shop Date:** {shop_date}  🛍️\n']
    for cat in sorted(categories):
        lines.append(f'• {cat}')

    message = "\n".join(lines)
    for chunk in chunk_message(message):
        await ctx.send(chunk)


async def fort_stats(ctx, player_name: str):
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

async def fort_map(ctx):
    print("COMMAND RECIEVED")

    map_data = fort_api.map.fetch()
    poi_image = map_data.poi_image
    today_date = datetime.now().strftime('%B %d, %Y')

    message = (f"**The Fortnite map on {today_date}:  📍**")
    await ctx.send(message)
    await ctx.send(poi_image)
    