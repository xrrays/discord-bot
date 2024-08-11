# blackjack.py

import random
import json
import os
import math
from datetime import datetime, timedelta

BALANCES_FILE = 'user_balances.json'
deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
user_balances = {}
last_gift_times = {}

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
    return user_balances.get(user_id)
    
def update_user_balance(user_id, amount):
    user_balances[user_id] += amount

def save_balances():
    with open(BALANCES_FILE, 'w') as f:
        json.dump(user_balances, f)

def load_balances():
    global user_balances
    if os.path.exists(BALANCES_FILE):
        with open(BALANCES_FILE, 'r') as f:
            try:
                loaded_balances = json.load(f)
                user_balances = {int(k): v for k, v in loaded_balances.items()}
            except json.JSONDecodeError:
                user_balances = {}
    else:
        user_balances = {}

async def print_balance(ctx, user_id):
    balance = get_user_balance(user_id)
    if balance == 0 or user_id not in user_balances:
        user_balances[user_id] = 100
        await ctx.send(f"You have **{get_user_balance(user_id)}** aura.  💎")
    else:
        await ctx.send(f"You have **{get_user_balance(user_id)}** aura.  💎")
    save_balances()

async def daily_gift(ctx):
    user_id = ctx.author.id
    current_time = datetime.now()

    if user_id not in user_balances:
        user_balances[user_id] = 100
    
    if user_id in last_gift_times:
        user_last_gift_time = last_gift_times[user_id]
        time_since_last = current_time - user_last_gift_time
        time_till_next = timedelta(seconds=60) - time_since_last

        if current_time - user_last_gift_time < timedelta(seconds=60):
            countdown = str(time_till_next).split('.')[0]
            await ctx.send(f'You can only claim this gift once every 60 seconds.\nClaim in: **{countdown}**...')
            last_gift_times_with_names = {ctx.guild.get_member(uid).name: bal for uid, bal in user_balances.items()}
            print(last_gift_times_with_names)
            return
    
    update_user_balance(user_id, 100)
    last_gift_times[user_id] = current_time
    await ctx.send(f'You have gained + 100 aura...  🎁\n**New Balance: {get_user_balance(user_id)}  💎**')
    save_balances()

async def show_leaderboard(ctx):
    user_balances_with_names = {ctx.guild.get_member(uid).name: bal for uid, bal in user_balances.items()}
    leaderboard = sorted(user_balances_with_names.items(), key=lambda item: item[1], reverse=True)

    leaderboard_message = '**🏆  LEADERBOARD:**\n'
    for idx, (user, balance) in enumerate(leaderboard, start=1):
        leaderboard_message += f"{idx}. {user}: {balance} aura  💎\n"

    await ctx.send(leaderboard_message)

async def play_blackjack(ctx):

    # BETTING SETUP
    user_id = ctx.author.id
    if user_id not in user_balances:
        user_balances[user_id] = 100
    balance = get_user_balance(user_id)
    if balance == 0:
        await ctx.send(f'You have no aura left **brokie!**')
        return
    await ctx.send(f'You have **{balance}** aura. How much would you like to bet?')

    while True:
        response = await ctx.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=59.0)
        try:
            bet = int(response.content)
            if bet < 1 or bet > balance:
                await ctx.send(f"Invalid amount. Please enter an amount between 1 and **{balance}**.")
            else:
                break
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
        
    user_balances_with_names = {ctx.guild.get_member(uid).name: bal for uid, bal in user_balances.items()}
    print(user_balances_with_names)
    save_balances()