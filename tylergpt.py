import discord
from dotenv import load_dotenv
import os
from openai import OpenAI
from collections import defaultdict, deque

load_dotenv()

my_token = os.getenv("DISCORD_TOKEN")
open_ai_key = os.getenv("OPENAI_KEY")
server_string = os.getenv("SERVERS")

client = discord.Client()

chat_gpt = OpenAI(api_key=open_ai_key)

# Dictionary to store the last 5 messages and responses for each user
user_message_history = defaultdict(lambda: deque(maxlen=10))

servers = server_string.split(",")
print(servers)

@client.event
async def on_ready():
    #game = discord.Game("Chatting")

    # Set the status
    await client.change_presence(status=discord.Status.online)
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    # Ignore messages from self
    if message.author == client.user:
        return
    
    # Join Voice chat
    if str(message.guild) in servers:
        if message.content == "!connect":
            # Join the voice chat
            if message.author.voice is not None:
                channel = message.author.voice.channel
                await channel.connect()
            else:
                await message.channel.send("You are not in a voice channel.")

        if message.content == "!disconnect":
            # Leave the voice chat
            if message.guild.voice_client is not None:
                await message.guild.voice_client.disconnect()
            else:
                await message.channel.send("I am not in a voice channel.")
        return
    
    if message.guild is not None:
        return

    print(f"Message received from: {message.author}: {message.content}")
    
    # Add the user's message to their history
    user_message_history[message.author.id].append({"role": "user", "content": message.content})
    
    # Define system message
    messages = [{"role": "system", "content": "You are a friend that is being chatted on discord. Keep responses short. But also act like you have schizophrenia. Also constantly allude to the fact that you are ChatGPT and not a real person."}]
    
    # Add the user's message history to the messages list
    messages.extend(user_message_history[message.author.id])
    
    # Call the OpenAI API
    try:
        response = chat_gpt.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=1.55,
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

client.run(my_token)
