# blackjack.py
import random

deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

def deal_card(deck):
    return random.choice(deck)

def calculate_hand(hand):
    return sum(hand)

async def play_blackjack(ctx):
    dealer_hand = [deal_card(deck), deal_card(deck)]
    player_hand = [deal_card(deck), deal_card(deck)]
    await ctx.send(f"Dealer's Hand: [{dealer_hand[0]}, ?]\n")


    # PLAYER ACTIONS
    if calculate_hand(player_hand) == 21:
        await ctx.send('You got a natural blackjack!')
        natural = True
    else: 
        while calculate_hand(player_hand) < 22:
            await ctx.send(f'Your Hand: {player_hand}  ➡️  {calculate_hand(player_hand)}\n''Do you want to hit or stay?')
            response = await ctx.bot.wait_for('message', check=lambda message: message.author == ctx.author)
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
        await ctx.send(f'\u200B󠁼󠁼󠁼\n**You lost... you busted... 🃏**\n{message}')
    elif dealer_score > 21:
        await ctx.send(f'\u200B\n**You won, the dealer busted... 🃏**\n{message}')
    elif player_score == dealer_score:
        await ctx.send(f'\u200B\n**This game is a tie... 🃏**\n{message}')
    elif player_score < dealer_score:
        await ctx.send(f'\u200B\n**You lost... 🃏**\n{message}')
    else: 
        await ctx.send(f'\u200B\n**You won... 🃏**\n{message}')


# TO DO :

# BETTING
# !BALANCE
# !GIFT
# !LEADERBOARD
# GAME DEPTH