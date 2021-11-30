# bot.py
# Copyright (c) 2021 War-Keeper

import os

import discord
from discord.utils import get
from discord import Intents
from dotenv import load_dotenv
from discord.ext.commands import Bot, has_permissions, CheckFailure
from better_profanity import profanity

profanity.load_censor_words()

# ----------------------------------------------------------------------------------------------
# Initializes the discord bot with a unique TOKEN and joins the bot to a server provided by the
# GUILD token. Handles bot shutdown and error events
# ----------------------------------------------------------------------------------------------

# Load the environment

load_dotenv()
# Get the token for our bot
TOKEN = os.getenv("TOKEN")
UNVERIFIED_ROLE_NAME = os.getenv("UNVERIFIED_ROLE_NAME")
# Set the bots intents to all
intents = Intents.all()
# Set all bot commands to begin with $
bot = Bot(intents=intents, command_prefix="$")

# ------------------------------------------------------------------------------------------------------------------
#    Function: on_guild_join()
#    Description: Activates when the bot joins a new guild, prints the name of the server it joins and the names of all members
#                 of that server
#    Inputs:
#    -guild which is bot is joining
#    Outputs:
#    -Success messages for channel creation and role creation
#    -Error if
# ------------------------------------------------------------------------------------------------------------------
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages and channel.name == "general":

            if "instructor-commands" not in guild.text_channels:
                await guild.create_text_channel("instructor-commands")
                await channel.send("instructor-commands channel has been added!")
            if "q-and-a" not in guild.text_channels:
                await guild.create_text_channel("q-and-a")
                await channel.send("q-and-a channel has been added!")
            if "verification" not in guild.text_channels:
                await guild.create_text_channel("verification")
                await channel.send("verification channel has been added!")

            if discord.utils.get(guild.roles, name="verified") is None:
                await guild.create_role(
                    name="verified", colour=discord.Colour(0x2ECC71), permissions=discord.Permissions.general()
                )
            if discord.utils.get(guild.roles, name="unverified") is None:
                await guild.create_role(
                    name="unverified", colour=discord.Colour(0xE74C3C), permissions=discord.Permissions.none()
                )
                unverified = discord.utils.get(guild.roles, name="unverified")
                # unverified members can only see/send messages in general channel until they verify
                overwrite = discord.PermissionOverwrite()
                overwrite.update(send_messages=True)
                overwrite.update(read_messages=True)
                await channel.set_permissions(unverified, overwrite=overwrite)
            if discord.utils.get(guild.roles, name="Instructor") is None:
                await guild.create_role(
                    name="Instructor", colour=discord.Colour(0x3498DB), permissions=discord.Permissions.all()
                )
            # Assign Verified role to Guild owner
            leader = guild.owner
            # leadrole = get(guild.roles, name="verified")
            unverified = discord.utils.get(guild.roles, name="unverified")
            # await leader.add_roles(leadrole, reason=None, atomic=True)
            # await channel.send(leader.name + " has been given verified role!")
            # Assign Instructor role to Guild owner
            leadrole = get(guild.roles, name="Instructor")
            await leader.add_roles(leadrole, reason=None, atomic=True)
            await channel.send(leader.name + " has been given Instructor role!")
            # Assign unverified role to all other members
            await leader.add_roles(leadrole, reason=None, atomic=True)
            for member in guild.members:
                await member.add_roles(unverified, reason=None, atomic=True)
            await channel.send('To verify yourself, send "$verify <FirstName LastName>" in the verification channel!')


# ------------------------------------------------------------------------------------------------------------------
#    Function: on_ready()
#    Description: Activates when the bot starts, prints the name of the server it joins and the names of all members
#                 of that server
#    Inputs:
#    -
#    Outputs:
#    -
# ------------------------------------------------------------------------------------------------------------------
@bot.event
async def on_ready():
    # guild = discord.utils.get(bot.guilds, name=GUILD)

    # print(
    #     f"{bot.user} is connected to the following guild:\n"
    #     f"{guild.name}(id: {guild.id})"
    # )

    # members = "\n -".join([member.name for member in guild.members])
    # print(f"Guild Members:\n - {members}")
    # db.connect()

    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
    bot.load_extension("jishaku")

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Over This Server"))
    print("READY!")


###########################
# Function: on_message
# Description: run when a message is sent to a discord the bot occupies
# Inputs:
#      - message: the message the user sent to a channel
###########################
@bot.event
async def on_message(message):
    """run on message sent to a channel"""
    # allow messages from test bot
    if message.author.bot and message.author.id == 889697640411955251:
        ctx = await bot.get_context(message)
        await bot.invoke(ctx)

    if message.author == bot.user:
        return

    if profanity.contains_profanity(message.content):
        await message.channel.send(message.author.name + " says: " + profanity.censor(message.content))
        await message.delete()

    await bot.process_commands(message)


###########################
# Function: on_message_edit
# Description: run when a user edits a message
# Inputs:
#      - before: the old message
#      - after: the new message
###########################
@bot.event
async def on_message_edit(before, after):
    """run on message edited"""
    if profanity.contains_profanity(after.content):
        await after.channel.send(after.author.name + " says: " + profanity.censor(after.content))
        await after.delete()


# ------------------------------------------------------------------------------------------
#    Function: on_member_join(member)
#    Description: Handles on_member_join events, DMs the user and asks for verification through newComer.py
#    Inputs:
#    - member: used to add member to the knowledge of the bot
#    Outputs:
#    -
# ------------------------------------------------------------------------------------------
@bot.event
async def on_member_join(member):

    unverified = discord.utils.get(member.guild.roles, name="unverified")  # finds the unverified role in the guild
    await member.add_roles(unverified)  # assigns the unverified role to the new member
    await member.send("Hello " + member.name + "!")
    await member.send(
        "Verify yourself before getting started! \n To use the verify command, send: $verify <your_full_name> \n \
        in the verification channel ( For example: $verify Jane Doe )"
    )


# ------------------------------------------------
#    Function: on_error(event, *args, **kwargs)
#    Description: Handles bot errors, prints errors to a log file
#    Inputs:
#    - member: event of the error
#    - *args: any arguments that come with error
#    - **kwargs: other args
#    Outputs:
#    -
# ------------------------------------------------
@bot.event
async def on_error(event, *args, **kwargs):
    with open("err.log", "a") as f:
        if event == "on_message":
            f.write(f"Unhandled message: {args[0]}\n")
        else:
            raise


# ----------------------------------
#    Function: on_member_join(member)
#    Description: Command for shutting down the bot
#    Inputs:
#    - ctx: used to access the values passed through the current context
#    Outputs:
#    -
# ----------------------------------
@bot.command(name="shutdown", help="Shuts down the bot, only usable by the owner")
@has_permissions(administrator=True)
async def shutdown(ctx):
    await ctx.send("Shutting Down bot")
    print("Bot closed successfully")
    ctx.bot.logout()
    exit()


# Starts the bot with the current token
bot.run(TOKEN)
