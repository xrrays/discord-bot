import random

deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

def deal_card(deck):
    return random.choice(deck)

def calculate_hand(hand):
    return sum(hand)

dealer_hand = [deal_card(deck), deal_card(deck)]
print(f"Dealer's Hand: [{dealer_hand[0]}, ?]")
player_hand = [deal_card(deck), deal_card(deck)]
print(f'Your Hand: {player_hand}\n')


# PLAYER ACTIONS
if calculate_hand(player_hand) == 21:
    print('You got a natural blackjack!')
    natural = True
else: 
    while calculate_hand(player_hand) < 22:
        action = input('Do you want to hit or stay? ').lower()
        if action == 'hit':
            player_hand.append(deal_card(deck))
            print(player_hand)
            if calculate_hand(player_hand) > 21:
                print("You busted everywhere... all over the place...\n")
        elif action == 'stay':
            print()
            break
        else:
            print("Invalid input. Pleaes type \"hit\" or \"stay\".")

# DEALER ACTIONS
while sum(dealer_hand) < 17: 
    new_card = random.choice(deck)
    dealer_hand.append(new_card)
    print('Dealer Hand', dealer_hand)
    if calculate_hand(dealer_hand) > 21:
        print("The dealer busted... everywhere...\n")

# GAME RESULTS
player_score = calculate_hand(player_hand)
dealer_score = calculate_hand(dealer_hand)

if player_score > 21:
    print('You lost... you busted...')
elif dealer_score > 21:
    print('You won, the dealer busted!')
elif player_score == dealer_score:
    print('The game is a tie.')
elif player_score < dealer_score:
    print('You lost...')
else: 
    print('You won!')

print('Final Scores:')
print(f'You: {player_hand} --> {calculate_hand(player_hand)}')
print(f'Dealer: {dealer_hand} --> {calculate_hand(dealer_hand)}')


