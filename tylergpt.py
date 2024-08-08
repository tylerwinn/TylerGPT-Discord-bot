import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os
from openai import OpenAI
from collections import defaultdict, deque
import datetime
import asyncio
import random

load_dotenv()

my_token = os.getenv("DISCORD_TOKEN")
open_ai_key = os.getenv("OPENAI_KEY")
server_string = os.getenv("SERVERS")

client = discord.Client()
chat_gpt = OpenAI(api_key=open_ai_key)

# Replace with actual user IDs
shit_list = [179130400508084225]
shit_list_system_prompt = [{"role": "system", "content": "You are reaching out to a friend on discord, use Gen-z and trendy slang."}]

# Dictionary to store the last 5 messages and responses for each user
user_message_history = defaultdict(lambda: deque(maxlen=10))

# Dictionary to store the last message time for shit list users
shit_list_last_message_time = {}

servers = server_string.split(",")
print(servers)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.change_presence(status=discord.Status.invisible)

@client.event
async def on_message(message):
    # Ignore messages from self
    if message.author == client.user:
        return

    # Check if the bot is mentioned in the message
    if message.guild is not None and client.user.mention not in message.content:
        return

    print(f"Message received from: {message.author}: {message.content}")

    # Add the user's message to their history
    user_message_history[message.author.id].append({"role": "user", "content": message.content})

    # Define system message
    messages = [{"role": "system", "content": "You Judas Iscariot. Respond as the real Judas Iscariot would have in his time."}]

    # Add the user's message history to the messages list
    messages.extend(user_message_history[message.author.id])

    # Call the OpenAI API
    try:
        response = chat_gpt.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        # Get ChatGPT's response
        reply = response.choices[0].message.content
        print(f"Response: {reply}")

        # Add the bot's response to the user's history
        user_message_history[message.author.id].append({"role": "assistant", "content": reply})

        # Wait for 3-10 seconds before sending the response
        await asyncio.sleep(random.uniform(3, 10))

        # Send the response to the user
        await message.channel.send(reply)
    except Exception as e:
        print(f"Error: {e}")

        # Send a base64 encoded message to the user if the API call fails
        await message.channel.send("VHlsZXIgaXMgZ29uZSwgYnV0IG1heWJlIGhlIHdhcyBuZXZlciBoZXJlIGF0IGFsbC4gWW91J3ZlIHdvbiwgZW5qb3kgaXQu")

client.run(my_token)
