# bot.py
# Copyright (c) 2021 War-Keeper

import os
import db
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
if __name__ == "__main__":
    # Load the environment
    CONN = db.setup()
    db.CONN = CONN
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
        if get(guild.roles, name="Instructor") is None:
            await guild.create_role(name="Instructor", colour=discord.Colour(0x2ecc71),
                                    permissions=discord.Permissions.all())
        if get(guild.roles, name="verified") is None:
            await guild.create_role(name="verified", colour=discord.Colour(0x2ecc71),
                                    permissions=discord.Permissions.general())
        if get(guild.roles, name="unverified") is None:
            await guild.create_role(name="unverified", colour=discord.Colour(0xe74c3c),
                                    permissions=discord.Permissions.none())
        
        unverified = get(guild.roles, name="unverified")
        
        verified = get(guild.roles, name="verified")
        
        Instructor = get( guild.roles, name="Instructor")
        
        general = get(guild.text_channels, name="general")
        
        # Default permissions for member roles.
        overwrites = {
            unverified: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            Instructor: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # If channels don't exist, create and set default permissions
        if 'instructor-commands' not in guild.text_channels:
            await guild.create_text_channel('instructor-commands', overwrites=overwrites)
            print("instructor-commands channel has been added!")
        if 'q-and-a' not in guild.text_channels:
            await guild.create_text_channel('q-and-a', overwrites=overwrites)
            print("q-and-a channel has been added!")
        if 'verification' not in guild.text_channels:
            await guild.create_text_channel('verification') # Everyone is allowed to read/write to verification channel
            print("verification channel has been added!")
        
        # Unverified members cannot send messages in general
        await general.set_permissions(unverified, send_messages=False)
            
        leader = guild.owner
        
        # Assign Instructor role to Guild owner
        await leader.add_roles(verified, reason=None, atomic=True)
        await leader.add_roles(Instructor, reason=None, atomic=True)
        print(leader.name + " has been given Instructor role!")
        
        # Add leader to name_mapping table
        # Using leader's username as real_name
        db.query('INSERT INTO name_mapping (guild_id, author_id, username, real_name) VALUES (%s, %s, %s, %s)',
                            (guild.id, leader.id, leader.name, leader.name))
        
        for member in guild.members:
            # If member is not the bot and the owner of the server.
            if member != guild.owner and member != guild.me:
                await member.add_roles(unverified, reason=None, atomic=True)
        print('member roles assigned')
        

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

        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="Over Your Server"
            )
        )
        print("READY!")

    ###########################
    # Function: on_message
    # Description: run when a message is sent to a discord the bot occupies
    # Inputs:
    #      - message: the message the user sent to a channel
    ###########################
    @bot.event
    async def on_message(message):
        ''' run on message sent to a channel '''
        # allow messages from test bot
        if message.author.bot and message.author.id == 889697640411955251:
            ctx = await bot.get_context(message)
            await bot.invoke(ctx)

        if message.author == bot.user:
            return

        if profanity.contains_profanity(message.content):
            await message.channel.send(message.author.name + ' says: ' +
                profanity.censor(message.content))
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
        ''' run on message edited '''
        if profanity.contains_profanity(after.content):
            await after.channel.send(after.author.name + ' says: ' +
                profanity.censor(after.content))
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
        verification = get(member.guild.text_channels, name='verification')
        unverified = discord.utils.get(
            member.guild.roles, name="unverified"
        )  # finds the unverified role in the guild
        await member.add_roles(unverified) # assigns the unverified role to the new member 
        await verification.send("Hello " + member.name + "!")
        await verification.send(
            "Verify yourself before getting started! \n Send the following command: $verify <your_full_name> \
            ( For example: $verify Jane Doe )")


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
        await ctx.send('Shutting Down bot')
        print("Bot closed successfully")
        ctx.bot.logout()
        exit()


    # Starts the bot with the current token
    bot.run(TOKEN)

