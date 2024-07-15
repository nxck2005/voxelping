# Import necessary libraries
import os
import discord
import datetime
import json
import requests

# Get the current date and time
now = datetime.datetime.now()
timePrefix = f'[{now}]:'

# Retrieve the Discord token from environment variables
token = os.getenv('DISCORD_TOKEN')

# Set up default intents and enable specific message intents for the bot
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True

# Create an instance of the bot with the specified intents
bot = discord.Bot(intents=intents)

# Event triggered when the bot is ready and connected to Discord
@bot.event
async def on_ready():
    print(f'Time: {now}')
    print(f'Logged in as {bot.user}')

# Event to handle incoming messages
@bot.event
async def on_message(message):
    # Log the command issued to the console
    print(f"{timePrefix} Command issued by {message.author}")
    # Ignore messages from the bot itself to prevent loops
    if message.author == bot.user:
        return
    
    # Respond to '$ping' command with bot latency
    if message.content.startswith('$ping'):
        await message.channel.send(f'Pong! {round(bot.latency * 1000, 2)} ms.')

# Event for handling slash commands to check server status
@bot.slash_command()
async def status(ctx, serverip: str):

    # Acknowledge the interaction to prevent timeout
    await ctx.defer()

    try:
        # URLs for server status API
        urlJavaStatus = f'https://api.mcsrvstat.us/simple/'
        returnedStatus = requests.get(f'{urlJavaStatus}{serverip}')
        rawServerInfo = requests.get(f'https://api.mcsrvstat.us/3/{serverip}')
        parsedServerInfo = rawServerInfo.json()
        
        # Log server info or failure to parse
        if parsedServerInfo:
            print(f"{timePrefix} Parsed server info for {serverip}")
        else:
            print(f"{timePrefix} Failed to parse server info for {serverip}.")

        # Embeds for server status messages
        failEmbed = discord.Embed(
            title = "VoxelPing",
            description = "Server status: **offline**",
            color = discord.Color.red()
        )

        passEmbed = discord.Embed(
            title = "VoxelPing",
            description = "Server status: **online**",
            color = discord.Color.green()
        )
        
        # Check and handle HTTP response status code
        if returnedStatus.status_code != 200:
            
            # Populate the fail embed with error information if the server is not reachable
            failEmbed.add_field(
                name = "",
                value = f"Couldn't resolve status for **{serverip}**. The server might be **offline** or invalid (404)."
            )
            failEmbed.add_field(
                name = "",
                value = f"Server IP: **{parsedServerInfo['ip']}**"
            )
            failEmbed.add_field(
                name = "",
                value = f"Hostname: **{parsedServerInfo['hostname']}**"
            )
            failEmbed.add_field(
                name = "",
                value = f"Port: **{parsedServerInfo['port']}**"
            )
            failEmbed.add_field(
                name = "",
                value = f"Status: **{parsedServerInfo['online']}**"
            )
            await ctx.respond(embed=failEmbed)
            return
        
        # Populate the pass embed with server information if online
        passEmbed.add_field(
            name = "",
            value = f"Server IP: **{parsedServerInfo['ip']}**"
        )
        passEmbed.add_field(
            name = "",
            value = f"Hostname: **{parsedServerInfo['hostname']}**"
        )
        passEmbed.add_field(
            name = "",
            value = f"Port: **{parsedServerInfo['port']}**"
        )
        passEmbed.add_field(
            name = "",
            value = f"Status: **Online**"
        )
        passEmbed.add_field(
            name = "",
            value = f"Version: **{parsedServerInfo['version']}**"
        )
        passEmbed.add_field(
            name = "",
            value = f"Players: **{parsedServerInfo['players']['online']}/{parsedServerInfo['players']['max']}**"
        )
        await ctx.respond(embed=passEmbed)
        return

    except Exception as e:
        # Handle any exceptions and log them
        print(f"{timePrefix} Exception occurred: {e}")
        await ctx.send("An error occurred while fetching the server status.")
        return

# Run the bot with the token
bot.run(token)
