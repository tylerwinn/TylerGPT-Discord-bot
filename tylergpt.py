import discord
from discord.ext import tasks
from dotenv import load_dotenv
import os
from openai import OpenAI
from collections import defaultdict, deque
import datetime
import asyncio

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

# Constants for checking shit list interval
CHECK_SHIT_LIST_INTERVAL_MINUTES = 3

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    #check_shit_list.start()

@client.event
async def on_message(message):
    # Ignore messages from self
    if message.author == client.user:
        return
    
    if message.guild is not None:
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
        
        # Send the response to the user
        await message.channel.send(reply)
    except Exception as e:
        print(f"Error: {e}")

        # Send a base64 encoded message to the user if the API call fails
        await message.channel.send("VHlsZXIgaXMgZ29uZSwgYnV0IG1heWJlIGhlIHdhcyBuZXZlciBoZXJlIGF0IGFsbC4gWW91J3ZlIHdvbiwgZW5qb3kgaXQu")

@tasks.loop(minutes=CHECK_SHIT_LIST_INTERVAL_MINUTES)
async def check_shit_list():
    print("Checking shit list users...")
    for user_id in shit_list:
        user = client.get_user(user_id)
        if user:
            now = datetime.datetime.now(datetime.timezone.utc)
            print(f"Found user: {user} with ID: {user.id}")
            if user.id not in shit_list_last_message_time or (now - shit_list_last_message_time[user.id]).total_seconds() > CHECK_SHIT_LIST_INTERVAL_MINUTES * 60:
                messages = shit_list_system_prompt.copy()
                if user.id in user_message_history:
                    messages.extend(user_message_history[user.id])
                else:
                    messages.append({"role": "user", "content": "Hey, what's up?"})

                try:
                    response = chat_gpt.chat.completions.create(
                        model="gpt-3.5-turbo",
                        temperature=1.55,
                        messages=messages
                    )

                    reply = response.choices[0].message.content
                    await user.send(reply)
                    print(f"Message sent to {user.id}: {reply}")
                    shit_list_last_message_time[user.id] = now
                except Exception as e:
                    print(f"Error sending message to {user_id}: {e}")
        else:
            print(f"User with ID {user_id} not found")
    await asyncio.sleep(1)  # Small delay to allow processing

client.run(my_token)
