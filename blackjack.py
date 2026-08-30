# blackjack.py

import asyncio
import logging
import math
import os
import random
from datetime import datetime, timedelta

import psycopg2


logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
STARTING_BALANCE = 100
AURA_BANK_UNAVAILABLE = "the aura bank's closed rn, try again later"

deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
last_gift_times = {}
ongoing_games = {}
game_lock = asyncio.Lock()
gift_lock = asyncio.Lock()


def deal_card(card_deck):
    return random.choice(card_deck)


def calculate_hand(hand):
    total = sum(hand)
    aces = hand.count(11)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total


def is_natural_blackjack(hand):
    return len(hand) == 2 and calculate_hand(hand) == 21


def dealer_should_hit(hand):
    return calculate_hand(hand) < 17


def determine_game_result(
    player_hand,
    dealer_hand,
    bet,
    *,
    player_natural=False,
    dealer_natural=False,
):
    """Return the result name and the single balance delta for a finished game."""
    player_natural = player_natural or is_natural_blackjack(player_hand)
    dealer_natural = dealer_natural or is_natural_blackjack(dealer_hand)

    if player_natural:
        if dealer_natural:
            return "push", 0
        return "natural", math.ceil(bet * 1.5)

    player_score = calculate_hand(player_hand)
    dealer_score = calculate_hand(dealer_hand)

    if player_score > 21:
        return "player_bust", -bet
    if dealer_score > 21:
        return "dealer_bust", bet
    if player_score == dealer_score:
        return "push", 0
    if player_score < dealer_score:
        return "loss", -bet
    return "win", bet


def _ensure_user_balance(cursor, user_id):
    cursor.execute(
        """
        INSERT INTO user_balances (user_id, balance)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO NOTHING;
        """,
        (user_id, STARTING_BALANCE),
    )


def get_user_balance(user_id):
    """Persist a new user's starting aura and return their current balance."""
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            _ensure_user_balance(cur, user_id)
            cur.execute(
                "SELECT balance FROM user_balances WHERE user_id = %s",
                (user_id,),
            )
            return cur.fetchone()[0]


def update_user_balance(user_id, amount):
    """Ensure the user exists, atomically apply a delta, and return the balance."""
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            _ensure_user_balance(cur, user_id)
            cur.execute(
                """
                UPDATE user_balances
                SET balance = balance + %s
                WHERE user_id = %s
                RETURNING balance;
                """,
                (amount, user_id),
            )
            return cur.fetchone()[0]


def get_all_balances():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, balance FROM user_balances")
            return cur.fetchall()


async def _get_balance(ctx, user_id):
    try:
        return await asyncio.to_thread(get_user_balance, user_id)
    except Exception as error:
        logger.error("Aura balance lookup failed (%s).", type(error).__name__)
        await ctx.send(AURA_BANK_UNAVAILABLE)
        return None


async def _change_balance(ctx, user_id, amount):
    try:
        return await asyncio.to_thread(update_user_balance, user_id, amount)
    except Exception as error:
        logger.error("Aura balance update failed (%s).", type(error).__name__)
        await ctx.send(AURA_BANK_UNAVAILABLE)
        return None


async def print_balance(ctx, user_id):
    balance = await _get_balance(ctx, user_id)
    if balance is not None:
        await ctx.send(f"You have **{balance}** aura.  💎")


async def daily_gift(ctx):
    user_id = ctx.author.id

    async with gift_lock:
        current_time = datetime.now()

        if user_id in last_gift_times:
            user_last_gift_time = last_gift_times[user_id]
            time_since_last = current_time - user_last_gift_time
            time_till_next = timedelta(seconds=60) - time_since_last

            if time_since_last < timedelta(seconds=60):
                countdown = str(time_till_next).split('.')[0]
                await ctx.send(
                    "You can only claim this gift once every 60 seconds.\n"
                    f"Claim in: **{countdown}**..."
                )
                return

        new_balance = await _change_balance(ctx, user_id, 100)
        if new_balance is None:
            return

        last_gift_times[user_id] = current_time
        await ctx.send(
            "You have gained +100 aura...  🎁\n"
            f"**New Balance: {new_balance}  💎**"
        )


async def show_leaderboard(ctx):
    try:
        user_balances = await asyncio.to_thread(get_all_balances)
    except Exception as error:
        logger.error("Aura leaderboard lookup failed (%s).", type(error).__name__)
        await ctx.send(AURA_BANK_UNAVAILABLE)
        return

    user_balances_with_names = {
        ctx.guild.get_member(uid).name: balance
        for uid, balance in user_balances
        if ctx.guild.get_member(uid)
    }

    leaderboard = sorted(
        user_balances_with_names.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    leaderboard_message = '**🏆  LEADERBOARD:**\n'
    for index, (user, balance) in enumerate(leaderboard, start=1):
        leaderboard_message += f"{index}. {user}: {balance} aura  💎\n"

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

    try:
        balance = await _get_balance(ctx, user_id)
        if balance is None:
            return
        if balance <= 0:
            await ctx.send(f'You have no aura left **brokie!**')
            return
        await ctx.send(f'You have **{balance}** aura. How much would you like to bet?')

        while True:
            try:
                response = await ctx.bot.wait_for(
                    'message',
                    check=lambda message: (
                        message.author == ctx.author
                        and message.channel == ctx.channel
                    ),
                    timeout=59.0,
                )
                bet = int(response.content)
                if bet < 1 or bet > balance:
                    await ctx.send(
                        "Invalid amount. Please enter an amount between 1 and "
                        f"**{balance}**."
                    )
                else:
                    break
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. The game has been canceled.")
                return
            except ValueError:
                await ctx.send("Please enter a valid number.")

        dealer_hand = [deal_card(deck), deal_card(deck)]
        player_hand = [deal_card(deck), deal_card(deck)]
        player_natural = is_natural_blackjack(player_hand)
        dealer_natural = is_natural_blackjack(dealer_hand)
        await ctx.send(f"Dealer's Hand: [{dealer_hand[0]}, ?]\n")

        if not player_natural:
            try:
                while calculate_hand(player_hand) < 22:
                    await ctx.send(
                        f'Your Hand: {player_hand}  ➡️  {calculate_hand(player_hand)}\n'
                        'Do you want to hit or stay?'
                    )
                    response = await ctx.bot.wait_for(
                        'message',
                        check=lambda message: (
                            message.author == ctx.author
                            and message.channel == ctx.channel
                        ),
                        timeout=59.0,
                    )
                    action = response.content.lower()
                    if action == 'hit':
                        player_hand.append(deal_card(deck))
                        if calculate_hand(player_hand) > 21:
                            await ctx.send(
                                "You busted... all over the place: "
                                f"{player_hand} ➡️ {calculate_hand(player_hand)}\n"
                            )
                    elif action == 'stay':
                        break
                    else:
                        await ctx.send('Invalid input. Pleaes type "hit" or "stay".')
            except asyncio.TimeoutError:
                await ctx.send("You took too long to respond. The game has been canceled.")
                return

        dealer_actions = []
        if calculate_hand(dealer_hand) > 17:
            dealer_actions.append(
                f'Dealer Hand: {dealer_hand}  ➡️  {calculate_hand(dealer_hand)}'
            )
        while dealer_should_hit(dealer_hand):
            dealer_hand.append(deal_card(deck))
            dealer_actions.append(
                f'Dealer Hand: {dealer_hand}  ➡️  {calculate_hand(dealer_hand)}'
            )
            if calculate_hand(dealer_hand) > 21:
                dealer_actions.append("The dealer busted... everywhere...\n")
                break
        if dealer_actions:
            await ctx.send("\n".join(dealer_actions))

        player_score = calculate_hand(player_hand)
        dealer_score = calculate_hand(dealer_hand)
        final_scores = (
            'Final Scores:\n'
            f'You: {player_hand}  ➡️  {player_score}\n'
            f'Dealer: {dealer_hand}  ➡️  {dealer_score}\n'
        )
        result, balance_delta = determine_game_result(
            player_hand,
            dealer_hand,
            bet,
            player_natural=player_natural,
            dealer_natural=dealer_natural,
        )

        if balance_delta:
            new_balance = await _change_balance(ctx, user_id, balance_delta)
        else:
            new_balance = await _get_balance(ctx, user_id)
        if new_balance is None:
            return

        if result == "natural":
            await ctx.send(
                f'You got a natural blackjack: {player_hand} \n'
                f'You gained {balance_delta} aura!'
            )
            await ctx.send(
                f'{final_scores}\n**New Balance: {new_balance}  💎**'
            )
        elif result == "player_bust":
            await ctx.send(
                f'\u200B\n**You lost... you busted...  🃏**\n{final_scores}'
                f'\n**New Balance: {new_balance}  💎**'
            )
        elif result == "dealer_bust":
            await ctx.send(
                f'\u200B\n**You won, the dealer busted...  🃏**\n{final_scores}'
                f'\n**New Balance: {new_balance}  💎**'
            )
        elif result == "push":
            await ctx.send(
                f'\u200B\n**This game is a tie...  🃏**\n{final_scores}'
                f'\n**New Balance: {new_balance}  💎**'
            )
        elif result == "loss":
            await ctx.send(
                f'\u200B\n**You lost...  🃏**\n{final_scores}'
                f'\n**New Balance: {new_balance}  💎**'
            )
        else:
            await ctx.send(
                f'\u200B\n**You won... 🃏**\n{final_scores}'
                f'\n**New Balance: {new_balance}  💎**'
            )
    except Exception as error:
        logger.error("Blackjack game ended unexpectedly (%s).", type(error).__name__)
        raise
    finally:
        async with game_lock:
            ongoing_games.pop(user_id, None)
