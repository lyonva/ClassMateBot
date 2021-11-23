# TODO deadline reminder for all students
# Copyright (c) 2021 War-Keeper
# This functionality provides various methods to manage reminders (in the form of creation, retrieval,
# updation and deletion)
# A user can set up a reminder, check what is due this week or what is due today.
# A user can also update or delete a reminder if needed.
import os
import asyncio
from datetime import datetime, timedelta
import sys
import discord
from discord.ext import commands
from utils import get_all_guild_names_by_id, is_instructor, is_dm, is_sm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

async def reminders_to_pages( reminders, guild_ids, guild_names ):
    total = len(guild_ids)
    pages = []
    for i, (name, id) in enumerate(zip(guild_names, guild_ids)):
        title = f"{name} ({i+1}/{total})"
        description = ""
        for guild_id, homework, due_date in reminders:
            if guild_id == id:
                description += f"{homework} is due {due_date}\n"
        if description == "":
            description = "Good news: no assignments due!"
        new_page = discord.Embed( 
            title = title,
            description = description,
            coluor = discord.Colour.orange(),
        )
        pages.append(new_page)
    
    return pages

async def send_manage_pages(ctx, pages):
    if len(pages) > 0:
        message = await ctx.send(embed = pages[0])
        await message.add_reaction('◀')
        await message.add_reaction('▶')
        
        def check(reaction, user):
            return user == ctx.author

        i = 0
        reaction = None
        
        while True:
            if str(reaction) == '◀':
                i -= 1
                i %= len(pages)
                await message.edit(embed = pages[i])
            elif str(reaction) == '▶':
                i += 1
                i %= len(pages)
                await message.edit(embed = pages[i])
            
            try:
                reaction, user = await ctx.bot.wait_for('reaction_add', timeout = 30.0, check = check)
            except Exception as e:
                print(e)
                break
    else:
        await ctx.send("Congratulations! You have no upcoming reminders.")


class Deadline(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.units = {"second": 1, "minute": 60, "hour": 3600, "day": 86400, "week": 604800, "month": 2592000}

    @commands.command(name="timenow",
                      help="Put in current time to get offset needed for proper."
                           "datetime notifications $timenow MMM DD YYYY HH:MM ex. $timenow SEP 25 2024 17:02")
    async def timenow(self, ctx, *, date: str):
        try:
            input_time = datetime.strptime(date, '%b %d %Y %H:%M')
        except ValueError:
            await ctx.send("Date could not be parsed")
            return

        utc_dt = datetime.utcnow()
        difference = utc_dt - input_time
        diff_in_hours = int(difference.total_seconds() / 3600)
        input_time += timedelta(hours=diff_in_hours)

        await ctx.send(f"Current time is {-diff_in_hours} hours from system time (UTC).")

    @timenow.error
    async def timenow_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "To use the timenow command (with current time), do: "
                "$timenow MMM DD YYYY HH:MM ex. $timenow SEP 25 2024 17:02")
        print(error)

    @commands.command(name="reminderadd", pass_context=True, aliases = ["ra"],
                      help="Add a reminder comprised of name and due date. $reminderadd HW_NAME MMM DD YYYY optional(HH:MM) "
                      "ex. $reminderadd HW2 SEP 25 2024 17:02")
    async def reminderadd(self, ctx, hwcount: str, *, date: str):
        """
            Function: reminderadd(self, ctx, hwcount: str, *, date: str)
            Description: Adds the homework to json in the specified format
            Inputs:
                - self: used to access parameters passed to the class through the constructor
                - ctx: used to access the values passed through the current context
                - hwcount: name of the homework
                - date: due date of the assignment
            Outputs: returns either an error stating a reason for failure or returns a success message
                    indicating that the reminder has been added
        """
        if is_sm(ctx):
            author = ctx.message.author
            await ctx.message.delete()
            
            try:
                duedate = datetime.strptime(date, '%b %d %Y %H:%M')
                # print(seconds)
            except ValueError:
                try:
                    duedate = datetime.strptime(date, '%b %d %Y')
                except ValueError:
                    await ctx.author.send("Due date could not be parsed")
                    return

            if is_instructor( ctx ):
                members = ctx.guild.members
            else:
                members = [ ctx.author ]
            sent = False
            for m in members:
                existing = db.query(
                    'SELECT * FROM reminders WHERE guild_id = %s AND homework = %s AND author_id = %s',
                    (ctx.guild.id, hwcount, m.id)
                )
                if not existing:
                    db.query(
                        'INSERT INTO reminders (guild_id, author_id, homework, due_date) VALUES (%s, %s, %s, %s)',
                        (ctx.guild.id, m.id, hwcount, duedate)
                    )
                    sent = True
            if sent:
                await ctx.author.send(
                    f"Homework: {hwcount} due on: {duedate} has been added.")
            else:
                await ctx.author.send("A homework under this name already exists.")
        else:
            await ctx.author.send( "This command can only be used inside a server." )

    @reminderadd.error
    async def reminderadd_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                'To use the reminderadd command, do: $reminderadd HW_NAME MMM DD YYYY optional(HH:MM) \n '
                '( For example: $reminderadd HW2 SEP 25 2024 17:02 )')



    @commands.command(name="reminderdelete", pass_context=True, aliases = ["rd"],
                      help="Delete a specific reminder using a homework name using "
                      "$reminderdelete HW_NAME ex. $reminderdelete HW2 ")
    async def reminderdelete(self, ctx, hwName: str):
        """
            Function: reminderdelete(self, ctx, hwName: str)
            Description: Delete a reminder using Classname and Homework name
            Inputs:
                - self: used to access parameters passed to the class through the constructor
                - ctx: used to access the values passed through the current context
                - hwName: name of the homework
            Outputs: returns either an error stating a reason for failure or
                returns a success message indicating that the reminder has been deleted
        """
        await ctx.message.delete()
        
        if is_sm(ctx):
            if is_instructor( ctx ):
                reminders_deleted = db.query(
                    'SELECT homework, due_date FROM reminders WHERE guild_id = %s AND homework = %s',
                    (ctx.guild.id, hwName)
                )
                db.query(
                    'DELETE FROM reminders WHERE guild_id = %s AND homework = %s',
                    (ctx.guild.id, hwName)
                )
            else:
                reminders_deleted = db.query(
                    'SELECT homework, due_date FROM reminders WHERE guild_id = %s AND homework = %s AND author_id = %s',
                    (ctx.guild.id, hwName, ctx.author.id)
                )
                db.query(
                    'DELETE FROM reminders WHERE guild_id = %s AND homework = %s AND author_id = %s',
                    (ctx.guild.id, hwName, ctx.author.id)
                )

            if len(reminders_deleted) > 0:
                await ctx.author.send(f"Reminders deleted.")
            else:
                await ctx.author.send(f"The chosen homework does not exist.")
        else:
            await ctx.author.send( "This command can only be used inside a server." )

    @reminderdelete.error
    async def reminderdelete_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                'To use the reminderdelete command, do: $reminderdelete HW_NAME \n '
                '( For example: $reminderdelete HW2 )')
        print(error)

    @commands.command(name="reminderedit", pass_context=True, aliases = ["re"],
                      help="Change the assignment date. $reminderedit HW_NAME MMM DD YYYY optional(HH:MM) "
                      "ex. $reminderedit HW2 SEP 25 2024 17:02 ")
    async def reminderedit(self, ctx, hwid: str, *, date: str):
        """
            Function: reminderedit(self, ctx, classid: str, hwid: str, *, date: str)
            Description: Update the 'Due date' for a homework by providing the classname and homewwork name
            Inputs:
            - self: used to access parameters passed to the class through the constructor
            - ctx: used to access the values passed through the current context
            - hwid: name of the homework
            - date: due date of the assignment
            Outputs: returns either an error stating a reason for failure or
                    returns a success message indicating that the reminder has been updated
        """
        if is_sm(ctx):
            author = ctx.message.author
            await ctx.message.delete()
            try:
                duedate = datetime.strptime(date, '%b %d %Y %H:%M')
            except ValueError:
                try:
                    duedate = datetime.strptime(date, '%b %d %Y')
                except ValueError:
                    await ctx.author.send("Due date could not be parsed")
                    return

            
            if is_instructor( ctx ):
                updated_reminders = db.query(
                    'SELECT due_date FROM reminders WHERE guild_id = %s AND homework = %s',
                    (ctx.guild.id, hwid)
                )
                db.query(
                    'UPDATE reminders SET due_date = %s WHERE guild_id = %s AND homework = %s',
                    (duedate, ctx.guild.id, hwid)
                )
            else:
                updated_reminders = db.query(
                    'SELECT due_date FROM reminders WHERE guild_id = %s AND homework = %s AND author_id = %s',
                    (ctx.guild.id, hwid, ctx.author.id)
                )
                db.query(
                    'UPDATE reminders SET due_date = %s WHERE guild_id = %s AND homework = %s AND author_id = %s',
                    (duedate, ctx.guild.id, hwid, ctx.author.id)
                )
            
            if len(updated_reminders) > 0:
                await ctx.author.send(f"{hwid} has been updated with following date: {duedate}")
            else:
                await ctx.author.send(f"The chosen homework does not exist.")
        else:
            await ctx.author.send( "This command can only be used inside a server." )

    @reminderedit.error
    async def reminderedit_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                'To use the reminderedit command, do: $reminderedit HW_NAME MMM DD YYYY optional(HH:MM) \n'
                ' ( For example: $reminderedit HW2 SEP 25 2024 17:02 )')
        print(error)
    
    @commands.command(name="duethisweek", pass_context=True, aliases = ["dw"],
                      help="check all the homeworks that are due this week.")
    async def duethisweek(self, ctx):
        """
            Function: duethisweek(self, ctx)
            Description: Displays all the homeworks that are due this week along with their due date
            Inputs:
                - self: used to access parameters passed to the class through the constructor
                - ctx: used to access the values passed through the current context
            Outputs: returns either an error stating a reason for failure
                    or returns a list of all the assignments that are due this week
        """
        if is_dm(ctx):
            reminders = db.query(
                "SELECT guild_id, homework, due_date "
                "FROM reminders "
                "WHERE author_id = %s AND date_part('day', due_date - now()) <= 7",
                (ctx.author.id,)
            )
            guild_ids = list(set([ r[0] for r in reminders ]))
            guild_names = get_all_guild_names_by_id(ctx, guild_ids)
            pages = await reminders_to_pages( reminders, guild_ids, guild_names )
            await send_manage_pages( ctx, pages )
        else:
            await ctx.message.delete()
            await ctx.author.send( "That command is DM only. Try DMing me." )

    @commands.command(name="duetoday", pass_context=True, aliases = ["dt"],
                    help="Check all the homeworks that are due today.")
    async def duetoday(self, ctx):
        """
            Function: duetoday(self, ctx)
            Description: Displays all the homeworks that are due today
            Inputs:
                - self: used to access parameters passed to the class through the constructor
                - ctx: used to access the values passed through the current context
            Outputs: returns either an error stating a reason for failure or
                        returns a list of all the assignments that are due on the day the command is run
        """
        if is_dm(ctx):
            reminders = db.query(
                "SELECT guild_id,homework, due_date::time AS due_time "
                "FROM reminders "
                "WHERE author_id = %s AND due_date::date = now()::date",
                (ctx.author.id,)
            )
            guild_ids = list(set([ r[0] for r in reminders ]))
            guild_names = get_all_guild_names_by_id(ctx, guild_ids)
            pages = await reminders_to_pages( reminders, guild_ids, guild_names )
            await send_manage_pages( ctx, pages )
        else:
            await ctx.message.delete()
            await ctx.author.send( "That command is DM only. Try DMing me." )
    

    @commands.command(name="reminders", pass_context=True, aliases = ["r"],
                      help="Lists all reminders.")
    async def reminders(self, ctx):
        """
            Function: reminders(self, ctx)
            Description: Print out all the reminders
            Inputs:
            - self: used to access parameters passed to the class through the constructor
            - ctx: used to access the values passed through the current context
            Outputs: returns either an error stating a reason for failure or
                    returns a list of all the assignments
        """
        if is_dm(ctx):
            author = ctx.message.author
            reminders = db.query(
                'SELECT guild_id, homework, due_date FROM reminders WHERE author_id = %s',
                (author.id,)
            )
            guild_ids = list(set([ r[0] for r in reminders ]))
            guild_names = get_all_guild_names_by_id(ctx, guild_ids)
            pages = await reminders_to_pages( reminders, guild_ids, guild_names )
            await send_manage_pages( ctx, pages )
        else:
            await ctx.message.delete()
            await ctx.author.send( "That command is DM only. Try DMing me." )
    
    
    @commands.command(name="remindersclear", pass_context=True, aliases = ["rc"],
                      help="Deletes all reminders.")
    async def remindersclear(self, ctx):
        """
            Function: remindersclear(self, ctx)
            Description: Delete all the reminders
            Inputs:
            - self: used to access parameters passed to the class through the constructor
            - ctx: used to access the values passed through the current context
            Outputs: returns either an error stating a reason for failure or
                    returns a success message stating that reminders have been deleted
        """
        if ctx.guild is None:
            db.query('DELETE FROM reminders WHERE author_id = %s', (ctx.author.id,))
            await ctx.author.send("All your reminders have been cleared.")
        else:
            await ctx.message.delete()
            db.query('DELETE FROM reminders WHERE author_id = %s AND guild_id = %s', (ctx.author.id,ctx.guild.id))
            await ctx.author.send("All your reminders from this server have been cleared.")

    # ---------------------------------------------------------------------------------
    #    Function: remindme(self, ctx, quantity: int, time_unit : str,*, text :str)
    #    Description: Personal remind me functionality
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    - quantity - time after which the data will be erased
    #    Outputs: returns either an error stating a reason for failure or
    #             returns a success message stating that reminders have been deleted
    # ---------------------------------------------------------------------------------

    # @commands.command(name="remindme", pass_context=True, help="Request the bot to set a reminder for a due date")
    # async def remindme(self, ctx, quantity: int, time_unit: str, *, text: str):

    #     time_unit = time_unit.lower()
    #     author = ctx.message.author
    #     s = ""
    #     if time_unit.endswith("s"):
    #         time_unit = time_unit[:-1]
    #         s = "s"
    #     if not time_unit in self.units:
    #         await ctx.send("Invalid unit of time. Select from seconds/minutes/hours/days/weeks/months")
    #         return
    #     if quantity < 1:
    #         await ctx.send("Quantity must not be 0 or negative")
    #         return
    #     if len(text) > 1960:
    #         await ctx.send("Text is too long.")
    #         return

    #     seconds = self.units[time_unit] * quantity
    #     future = int(time.time() + seconds)
    #     # TODO set timestamp compatible with db

    #     db.query(
    #         'INSERT INTO reminders (guild_id, author_id, future, text) VALUES (%s, %s, %s)',
    #         (ctx.guild.id, author.id, future, text)
    #     )

    #     await ctx.send("I will remind you that in {} {}.".format(str(quantity), time_unit + s))

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     await ctx.send('Unidentified command..please use $help to get the list of available commands')

    async def delete_old_reminders(self):
        """
            Function: delete_old_reminders(self)
            Description: asynchronously keeps on tracking the database for expired reminders and cleans them.
            Inputs:
            - self: used to access parameters passed to the class through the constructor
        """
        while self is self.bot.get_cog("Deadline"):
            db.query('DELETE FROM reminders WHERE now() > due_date')
            await asyncio.sleep(10)


# -------------------------------------
# add the file to the bot's cog system
# -------------------------------------
def setup(bot):
    n = Deadline(bot)
    loop = asyncio.get_event_loop()
    # TODO
    loop.create_task(n.delete_old_reminders())
    bot.add_cog(n)
