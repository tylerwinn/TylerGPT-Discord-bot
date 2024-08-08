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
flesh_server_id = int(os.getenv("FLESH_SERVER_ID"))  # Add Flesh's Server ID to your .env file

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
    schedule_daily_deletion.start()

@client.event
async def on_message(message):
    # Command to delete messages in Flesh's server
    if message.guild is not None and message.guild.id == flesh_server_id and message.content.lower() == '!deletemessages':
        await delete_all_messages(client.user)
        return
    
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

async def delete_all_messages(user):
    await delete_messages_in_servers(user)
    await delete_messages_in_dms(user)

async def delete_messages_in_servers(user):
    for guild in client.guilds:
        if guild.id == flesh_server_id:
            continue
        for channel in guild.text_channels:
            try:
                async for message in channel.history(limit=200):
                    if message.author == user:
                        try:
                            print(message.content)
                            await message.delete()
                        except discord.Forbidden:
                            print(f"Missing permissions to delete message in {channel.name} of {guild.name}")
                        except Exception as e:
                            print(f"Failed to delete message in {channel.name} of {guild.name}: {e}")
            except discord.Forbidden:
                print(f"Missing permissions to read messages in {channel.name} of {guild.name}")
            except Exception as e:
                print(f"Failed to read messages in {channel.name} of {guild.name}: {e}")

async def delete_messages_in_dms(user):
    for dm_channel in client.private_channels:
        if isinstance(dm_channel, discord.DMChannel):
            try:
                async for message in dm_channel.history(limit=200):
                    if message.author == user:
                        try:
                            print(message.content)
                            await message.delete()
                        except discord.Forbidden:
                            print(f"Missing permissions to delete DM message")
                        except Exception as e:
                            print(f"Failed to delete DM message: {e}")
            except discord.Forbidden:
                print(f"Missing permissions to read DM messages")
            except Exception as e:
                print(f"Failed to read DM messages: {e}")

@tasks.loop(hours=24)
async def schedule_daily_deletion():
    now = datetime.datetime.now()
    target_time = datetime.datetime.combine(now.date(), datetime.time(0, 0))
    if now > target_time:
        target_time += datetime.timedelta(days=1)
    await asyncio.sleep((target_time - now).total_seconds())
    await delete_all_messages(client.user)

client.run(my_token)
