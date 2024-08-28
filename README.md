# Personal Discord Bot
This is a personal discord bot for my friends and I that provides games, information and other random features. The bot runs 24/7 with the use of a cloud hosting servcice, uses PostGresSQL to track user balances for blackjack and is connected straight to this GitHub so updates can be deployed to the bot seamlessly.

## Features
### Blackjack System
#### Commands: !blackjack, !leaderboard, !gift, !balance
A blackjack feature supported by a system revolving around the use of a made up currency. Currency is gifted by the bot, on a chosen cooldown, for players to play with. The currency is then used in a game against the dealer in a game of blackjack to be won or lost. The user's balance can be checked and is tracked against the other players on the server wide leaderboard.

### Character AI Chatbot
#### Commands: !chat
#### Characters Supported: ChatGPT, Deku, TikTok Brainrot, Who Would Win, Sukuna, Nami, Psychologist, Adventure Game, Homelander
A chatbot feature that supports several characters that the user can have a conversation with, in their character. The bot uses the website Character AI and an API to access these characters and relay the conversation between the user and the character in real time. Characters can easily be added and removed from the bot's roster with a simple line of code giving the feature many useful implementations, including for educational help, creative assistance, humorous chats and more.

### Fortnite Information
#### Commands: !news, !shop, !map, !stats playerName
The bot uses the Fortnite API to fetch and relay data from Fortnite to the user. The data that the user can request includes current Fortnite news, the skins currently in the Fortnite item shop and their prices, an image of what the Fortnite map currently looks like and the statistics of any player, including their kills, deathes, wins and time played.

### Others
#### Commands: !weather cityName, !joke, !goat
The weather command provides the user with the current weather and timezone information about any city in the world.  
The joke command returns a random joke to the user, from different categories like puns, dark humor and others.  
The goat command makes the bot send a random GIF of LeBron James.  

## API's Used
FORTNITE API: https://github.com/Fortnite-API/py-wrapper  
WEATHER API: https://www.weatherapi.com/  
JOKE API : https://github.com/benjhar/JokeAPI-Python#readme  
GIPHY API: https://developers.giphy.com/dashboard/  
CHARACTER AI API: https://github.com/kramcat/CharacterAI  

## Future Additions
- image generation (!image prompt)
- information about a movie, ie. reviews, box office, budget, release date (!movie movieName)
- quote bank that we can add to, bot sends one random quote a day (!quoteadd)
- top news headlines (!headlines)
- currency converter (!convert)
- any other random additions/improvements that seem interesting/useful

