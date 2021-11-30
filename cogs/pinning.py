# TODO privately pin a message based on copying a message link from a channel
# Copyright (c) 2021 War-Keeper
# This functionality lets the students pin the messages they want to.
# The bot personally pins the messages, i.e. the user can only see his pinned messages and not of others.
# The messages could be arranged on the basis of tags which the user can himself/herself give to the messages.
import os
import sys

from discord.ext import commands

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db
import utils


class Pinning(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Test command to check if the bot is working
    @commands.command()
    async def helpful3(self, ctx):
        await ctx.author.send(f"Pong! My ping currently is {round(self.bot.latency * 1000)}ms")



    @commands.command(name="pin", help="Pin a message by adding a tagname (single word) and a description(can be multi word).")
    async def addMessage(self, ctx, tagname: str, *, description: str):

        """
        Function: addMessage(self, ctx, tagname: str, *, description: str)
        Description: Used to pin a message by the user. The message gets stored in a JSON file in the required format.
        Inputs:
        - self: used to access parameters passed to the class through the constructor
        - ctx: used to access the values passed through the current context
        - tagname: a tag given by the user to their pinned message.
        - description: description of the pinned message given by the user.
        Outputs: Adds pinned message to DB.
       """

        if utils.is_dm(ctx):
            author = ctx.message.author
            result = await utils.chooseGuild(self, ctx)

            servers = result[0]
            res = result[1]

            db.query(
                'INSERT INTO pinned_messages (guild_id, author_id, tag, description) VALUES (%s, %s, %s, %s)',
                (servers[res - 1], author.id, tagname, description)
            )

            await ctx.author.send(
                f"A new message has been pinned with tag: {tagname} and description: {description}")
        else:
            await ctx.message.delete()
            await ctx.author.send("$pin command is DM only. Try sending it as a DM!")

    @addMessage.error
    async def addMessage_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                "To use the pin command, do: $pin TAGNAME DESCRIPTION \n ( For example: $pin HW8 <link to message> HW8 reminder )")
        print(error)




    @commands.command(name="unpin", help="Unpin a message by passing the tagname.")
    async def deleteMessage(self, ctx, tagname: str):


        """
        Function: deleteMessage(self, ctx, tagname: str, *)
        Description: This command unpins the pinned messages with the provided tagname.
        Inputs:
        - self: used to access parameters passed to the class through the constructor
        - ctx: used to access the values passed through the current context
        - tagname: the tag used to identify which pinned messages are to be deleted.
        Outputs: Remove pinned message from DB.
        """

        if utils.is_dm(ctx):
            author = ctx.message.author

            result = await utils.chooseGuild(self, ctx)

            servers = result[0]
            res = result[1]


            rows_deleted = db.query(
                'SELECT * FROM pinned_messages WHERE guild_id = %s AND tag = %s AND author_id = %s',
                (servers[res - 1], tagname, author.id)
            )
            db.query(
                'DELETE FROM pinned_messages WHERE guild_id = %s AND tag = %s AND author_id = %s',
                (servers[res - 1], tagname, author.id)
            )

            if len(rows_deleted) == 0:
                await ctx.author.send(
                    f"No message found with the combination of tagname: {tagname}, and author: {author}.")
            else:
                await ctx.author.send(
                    f"{len(rows_deleted)} pinned message(s) has been deleted with tag: {tagname}.")
        else:
            await ctx.message.delete()
            await ctx.author.send('$unpin is a DM only command. Try sending it as a DM!')

    @deleteMessage.error
    async def deleteMessage_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                'To use the unpin command, do: $unpin TAGNAME \n ( For example: $unpin HW8 )')
        print(error)


    @commands.command(name="pinnedmessages", help="Retrieve the pinned messages by a particular tag or all messages.")
    async def retrieveMessages(self, ctx, tagname: str = ""):

        """
        Function: retrieveMessages(self, ctx, tagname: str)
        Description: This command is used to retrieve all the pinned messages under a
                        given tagname by a particular user, or all messages if tag is empty.
        Inputs:
        - self: used to access parameters passed to the class through the constructor
        - ctx: used to access the values passed through the current context
        - tagname: the tag used to identify which pinned messages are to be retrieved.
        Outputs: Retrieves pinned messages from DB.
        """
        if utils.is_dm(ctx):
            author = ctx.message.author

            result = await utils.chooseGuild(self, ctx)
            servers = result[0]
            res = result[1]

            if tagname == "":
                messages = db.query(
                    'SELECT tag, description FROM pinned_messages WHERE guild_id = %s AND author_id = %s',
                    (servers[res - 1], author.id)
                )
            else:
                messages = db.query('SELECT tag, description FROM pinned_messages WHERE guild_id = %s AND author_id = %s AND tag = %s',(servers[res - 1], author.id, tagname))
                
            if len(messages) == 0:
                await ctx.author.send("No messages found with the given tagname and author combination")
            for tag, description in messages:
                await ctx.author.send(f"Tag: {tag}, Description: {description}")
        else:
            await ctx.message.delete()
            await ctx.author.send("$pinnedmessages is a DM only command! Try sending a DM")


    @retrieveMessages.error
    async def retrieveMessages_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                "To use the pinnedmessages command, do: $pinnedmessages:"
                " TAGNAME \n ( For example: $pinnedmessages HW8 )")
        print(error)



    @commands.command(name="updatepin", help="Update a previously pinned message by passing the tagname and old description in the same order")
    async def updatePinnedMessage(self, ctx, tagname: str, *, description: str):
        """
        Function: updatePinnedMessage(self, ctx, tagname: str, *, description: str)
        Description: This is used to update a pinned message with a given tagname. Deletes old messages for the tag.
        Inputs:
        - self: used to access parameters passed to the class through the constructor
        - ctx: used to access the values passed through the current context
        - tagname: tag to be updated
        - description: new description
        Outputs: Updates pinned message to DB.
        """
        if utils.is_dm(ctx):
            await ctx.invoke(self.bot.get_command('unpin'), tagname)
            await ctx.invoke(self.bot.get_command('pin'), tagname=tagname, description=description)
        else:
            await ctx.message.delete()
            await ctx.author.send("$updatepin is a DM only command! Try sending a DM")

    @updatePinnedMessage.error
    async def updatePinnedMessage_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                "To use the updatepin command, do: $pin TAGNAME DESCRIPTION \n ( $updatepin HW8 <link to message> HW8 reminder )")
        print(error)


# -------------------------------------
# add the file to the bot's cog system
# -------------------------------------
def setup(bot):
    n = Pinning(bot)
    bot.add_cog(n)
