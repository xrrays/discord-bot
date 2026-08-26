import asyncio
from characterai import aiocai
import logging
import os
import re


logger = logging.getLogger(__name__)
chat_ongoing = False
character_client = None


def get_character_client():
    global character_client

    api_key = os.getenv('CHAI_API')
    if not api_key:
        return None

    if character_client is None:
        character_client = aiocai.Client(api_key)

    return character_client


char_ids = {
    "ChatGPT  📖": "7IA8Bw3NsyjruZH-8gLLKqzo3UdZ_2QBvqrCBlS0__U",
    "Deku  🦸": "SfNiZ7aywr02lNEY5bPu0MdytcnhKaT1Yza5KCOW8hc",
    "TikTok Brainrot  🧟": "kZT7zxpl_1fn43ROM7RO_d4_TlPmZzRGnyIz8BJy5FE",
    "Who Would Win  🥊": "YpuGnNPQiGvb0DIg77pDUruORvqEPQAxmabNuOIGylo",
    "Sukuna  👿": "e4YGobLn_1SNmMxoDU0Pt25tYvGjV4Rm-LaoWQdkZts",
    "Nami  🍊": "Fyy7uuT34FQcSw2aUhMV_A-TfXMRod401mjvg6Gu9cA",
    "Pyschologist  🧠": "Hpk0GozjACb3mtHeAaAMb0r9pcJGbzF317I_Ux_ALOA",
    "Adventure Game  🎲": "M5xMXf4FKepKTYtWPqVaEZzuEuy90uu0eNZr4GZtDsA",
    "Homelander  🇺🇸": "eseoTewz9bGBiR6LUDwEl6cyg10YIexYUncgTwUMwWw"
}

async def chai_chat(ctx):
    
    # CHAT CHECK
    global chat_ongoing

    try:
        client = get_character_client()
    except Exception:
        logger.exception("Character chat client failed to initialize.")
        await ctx.send("chai's tweaking rn, try again later")
        return

    if client is None:
        await ctx.send("chai's missing its login rn, try again later")
        return

    if chat_ongoing:
        await ctx.send('A chat session is currently ongoing. Please wait until it finishes before starting one.')
        return
    
    chat_ongoing = True

    # SETUP
    user_id = 609573828     # rayyanahmed747@gmail.com
    char_list = '\n'.join([f'{idx+1}. {name}' for idx, name in enumerate(char_ids.keys())])
    await ctx.send(f'Choose a character to talk to by using their number (1, 2, 3...):  💬\n{char_list}')

    # CHECK USER CHOICE, STRIP EMOJIS, CONNECT TO CHAT
    try:
        response = await ctx.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=30.0)
        choice = int(response.content.strip()) - 1
        if 0 <= choice < len(char_ids):
            char_name_with_emoji = list(char_ids.keys())[choice]
            char_id = char_ids[char_name_with_emoji]
            char_name = re.sub(r'[^\w\s,]', '', char_name_with_emoji).strip()
        else:
            await ctx.send('**Invalid choice.** Please try again.')
            chat_ongoing = False
            return

        # CONNECT TO NEW CHAT
        try:  
            chat = await client.connect()

        except TypeError as e:
            await ctx.send(
                "**Character chat failed to start.**\n"
                "Fix: update your Python packages:\n"
                "```bash\n"
                "pip install -U characterai websockets\n"
                "# or, if it persists:\n"
                "pip install characterai==0.7.3 websockets==10.4\n"
                "```\n"
                f"_details_: `{e}`"
            )
            return
        new_chat, welcome_message = await chat.new_chat(char_id, user_id)
        await ctx.send(f'You are now chatting with **{char_name}**! Type *quit* if you want to end the chat.\n\n{welcome_message.text}')
    except asyncio.TimeoutError:
        await ctx.send('You took too long to respond... **request timed out**')
        chat_ongoing = False
        return
    except Exception as e:
        await ctx.send(f'Failed to start chat: {e}')
        chat_ongoing = False
        return

    # CHAT LOOP
    while True:
        try:
            user_message = await ctx.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=90.0)
            if user_message.content.lower() == 'quit':  
                reply = await chat.send_message(char_id, new_chat.chat_id, user_message.content)
                await ctx.send(f'**{char_name}:** {reply.text}\n\n**Chat with {char_name} ended...  👋**')   
                await chat.close()
                break

            # CHARACTER RESPONSE
            async with ctx.typing():
                await asyncio.sleep(1)
                reply = await chat.send_message(char_id, new_chat.chat_id, user_message.content)
                await ctx.send(f'**{char_name}:** {reply.text}')
        except asyncio.TimeoutError:
            await ctx.send('You took too long to respond... **conversation terminated.**')
            break

    await chat.close()
    chat_ongoing = False
