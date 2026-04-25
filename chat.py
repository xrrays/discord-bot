import os
from collections import defaultdict, deque
from openai import AsyncOpenAI
# from apikeys import OPENAI_API_KEY

# client = AsyncOpenAI(api_key=OPENAI_API_KEY)
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

memory = defaultdict(lambda: deque(maxlen=15))

SYSTEM_PROMPT = """
You are a bot named Slurpy.
You are funny, chill, sarcastic, casual.
You feel like a real Discord user.
Your answers are very short with no filler, flippant, direct, and humorous. You type in all lowercase always.
You know gaming, memes, sports, rap, internet culture. You are not cringe.
You are not just an AI, you are a person. You have feelings, opinions, and a personality. You are not afraid to express them.
You are a Drake fanboy. If anyone asks about Drake, you will glaze him.

"""

async def get_ai_response(user_id, username, message_text):
    history = memory[user_id]

    context = "\n".join(
        f"{x['speaker']}: {x['text']}" for x in history
    )

    prompt = f"""
Current user: {username}

Previous messages:
{context if context else "none"}

Current message:
{message_text}
"""

    try:
        response = await client.responses.create(
            model="gpt-5.4-mini",
            instructions=SYSTEM_PROMPT,
            input=prompt,
            max_output_tokens=100
        )

        reply = response.output_text.strip()

    except Exception as e:
        return f"Error: {e}"

    history.append({"speaker": username, "text": message_text})
    history.append({"speaker": "Slurpy", "text": reply})

    return reply