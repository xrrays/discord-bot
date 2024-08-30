# blackjack.py

import random
import os
import psycopg2
import math
import asyncio
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL")
deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
last_gift_times = {}
ongoing_games = {}
game_lock = asyncio.Lock()

def deal_card(deck):
    return random.choice(deck)

def calculate_hand(hand):
    total = sum(hand)
    aces = hand.count(11)

    while total > 21 and aces:
        total -= 10
        hand[hand.index(11)] = 1
        aces -= 1
    
    return total

def get_user_balance(user_id):
    # Connect to database, fetch balance associated with user id
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM user_balances WHERE user_id = %s", (user_id,))
            result = cur.fetchone()
            return result[0] if result else 100
    
def update_user_balance(user_id, amount):
    # Connect to databse, insert user id and associated balance
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO user_balances (user_id, balance) 
            VALUES (%s, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET balance = user_balances.balance + EXCLUDED.balance; """, (user_id, amount))

async def print_balance(ctx, user_id):
    balance = get_user_balance(user_id)
    await ctx.send(f"You have **{balance}** aura.  💎")

async def daily_gift(ctx):
    user_id = ctx.author.id
    current_time = datetime.now()

    if user_id in last_gift_times:
        user_last_gift_time = last_gift_times[user_id]
        time_since_last = current_time - user_last_gift_time
        time_till_next = timedelta(seconds=60) - time_since_last

        if current_time - user_last_gift_time < timedelta(seconds=60):
            countdown = str(time_till_next).split('.')[0]
            await ctx.send(f'You can only claim this gift once every 60 seconds.\nClaim in: **{countdown}**...')
            return
    
    update_user_balance(user_id, 100)
    last_gift_times[user_id] = current_time
    await ctx.send(f'You have gained +100 aura...  🎁\n**New Balance: {get_user_balance(user_id)}  💎**')

async def show_leaderboard(ctx):
    # Connect to database, fetch ALL balances
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, balance FROM user_balances")
            user_balances = cur.fetchall()      # Returns a list of tuples [(user_id, 100), (user_id, 200)...]

    user_balances_with_names = {                # Convert tuples to a dictionary, also check if user exists
        ctx.guild.get_member(uid).name: bal 
        for uid, bal in user_balances 
        if ctx.guild.get_member(uid)  }
    
    leaderboard = sorted(user_balances_with_names.items(), key=lambda item: item[1], reverse=True)

    leaderboard_message = '**🏆  LEADERBOARD:**\n'
    for idx, (user, balance) in enumerate(leaderboard, start=1):
        leaderboard_message += f"{idx}. {user}: {balance} aura  💎\n"

    await ctx.send(leaderboard_message)

async def play_blackjack(ctx):

    user_id = ctx.author.id
    async with game_lock:
        if ongoing_games.get(user_id):
            await ctx.send(f"You're **already** in a game, finish it!")
            return
        
        if ongoing_games:
            await ctx.send(f"Someone is in a game right now, **wait!**")
            return
        
        ongoing_games[user_id] = True

    # BETTING SETUP
    try:
        balance = get_user_balance(user_id)
        if balance == 0:
            await ctx.send(f'You have no aura left **brokie!**')
            return
        await ctx.send(f'You have **{balance}** aura. How much would you like to bet?')

        while True:
            try:
                response = await ctx.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=59.0)
                bet = int(response.content)
                if bet < 1 or bet > balance:
                    await ctx.send(f"Invalid amount. Please enter an amount between 1 and **{balance}**.")
                else:
                    break
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. The game has been canceled.")
                return
            except ValueError:
                await ctx.send("Please enter a valid number.")

        # GAME SETUP
        dealer_hand = [deal_card(deck), deal_card(deck)]
        player_hand = [deal_card(deck), deal_card(deck)]
        await ctx.send(f"Dealer's Hand: [{dealer_hand[0]}, ?]\n")

        # PLAYER ACTIONS
        if calculate_hand(player_hand) == 21:
            winnings = math.ceil(bet * 1.5)
            update_user_balance(user_id, winnings)
            await ctx.send(f'You got a natural blackjack: {player_hand} \nYou gained {winnings} aura!')
        else: 
            try:
                while calculate_hand(player_hand) < 22:
                    await ctx.send(f'Your Hand: {player_hand}  ➡️  {calculate_hand(player_hand)}\n''Do you want to hit or stay?')
                    response = await ctx.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=59.0)
                    action = response.content.lower()
                    if action == 'hit':
                        player_hand.append(deal_card(deck))
                        if calculate_hand(player_hand) > 21:
                            await ctx.send(f"You busted... all over the place: {player_hand} ➡️ {calculate_hand(player_hand)}\n")
                    elif action == 'stay':
                        break
                    else:
                        await ctx.send("Invalid input. Pleaes type \"hit\" or \"stay\".")
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. The game has been canceled.")
                return

        # DEALER ACTIONS
        dealer_actions = []
        if sum(dealer_hand) > 17:
            dealer_actions.append(f'Dealer Hand: {dealer_hand}  ➡️  {calculate_hand(dealer_hand)}')
        while sum(dealer_hand) < 17: 
            new_card = random.choice(deck)
            dealer_hand.append(new_card)
            dealer_actions.append(f'Dealer Hand: {dealer_hand}  ➡️  {calculate_hand(dealer_hand)}')
            if calculate_hand(dealer_hand) > 21:
                dealer_actions.append("The dealer busted... everywhere...\n")
                break
        if dealer_actions:
            await ctx.send("\n".join(dealer_actions))

        # GAME RESULTS
        player_score = calculate_hand(player_hand)
        dealer_score = calculate_hand(dealer_hand)
        message =  (f'Final Scores:\n'
                    f'You: {player_hand}  ➡️  {calculate_hand(player_hand)}\n'
                    f'Dealer: {dealer_hand}  ➡️  {calculate_hand(dealer_hand)}\n')

        if player_score > 21:
            update_user_balance(user_id, -bet)
            await ctx.send(f'\u200B󠁼󠁼󠁼\n**You lost... you busted...  🃏**\n{message}'
                            f'\n**New Balance: {get_user_balance(user_id)}  💎**')
        
        elif dealer_score > 21:
            update_user_balance(user_id, bet)
            await ctx.send(f'\u200B\n**You won, the dealer busted...  🃏**\n{message}'
                        f'\n**New Balance: {get_user_balance(user_id)}  💎**')

        elif player_score == dealer_score:
            await ctx.send(f'\u200B\n**This game is a tie...  🃏**\n{message}'
                        f'\n**New Balance: {get_user_balance(user_id)}  💎**')

        elif player_score < dealer_score:
            update_user_balance(user_id, -bet)
            await ctx.send(f'\u200B\n**You lost...  🃏**\n{message}'
                        f'\n**New Balance: {get_user_balance(user_id)}  💎**')

        else: 
            update_user_balance(user_id, bet)
            await ctx.send(f'\u200B\n**You won... 🃏**\n{message}'
                        f'\n**New Balance: {get_user_balance(user_id)}  💎**')
    finally:    
        async with game_lock:
            del ongoing_games[user_id]