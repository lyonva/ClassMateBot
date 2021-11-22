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
from utils import get_all_guild_names_by_id

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
                      help="put in current time to get offset needed for proper "
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

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: duedate(self, ctx, hwcount: str, *, date: str)
    #    Description: Adds the homework to json in the specified format
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    - hwcount: name of the homework
    #    - date: due date of the assignment
    #    Outputs: returns either an error stating a reason for failure or returns a success message
    #          indicating that the reminder has been added
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(name="addhw",
                      help="add homework and due-date $addhw HW_NAME MMM DD YYYY optional(HH:MM) "
                      "ex. $addhw HW2 SEP 25 2024 17:02")
    async def duedate(self, ctx, hwcount: str, *, date: str):
        author = ctx.message.author

        try:
            duedate = datetime.strptime(date, '%b %d %Y %H:%M')
            # print(seconds)
        except ValueError:
            try:
                duedate = datetime.strptime(date, '%b %d %Y')
            except ValueError:
                await ctx.send("Due date could not be parsed")
                return

        existing = db.query(
            'SELECT * FROM reminders WHERE guild_id = %s AND homework = %s',
            (ctx.guild.id, hwcount)
        )
        if not existing:
            db.query(
                'INSERT INTO reminders (guild_id, author_id, homework, due_date) VALUES (%s, %s, %s, %s)',
                (ctx.guild.id, author.id, hwcount, duedate)
            )
            await ctx.send(
                f"A date has been added for: homework named: {hwcount} "
                f"which is due on: {duedate} by {author}.")
        else:
            await ctx.send("This homework has already been added..!!")

    @duedate.error
    async def duedate_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                'To use the addhw command, do: $addhw CLASSNAME HW_NAME MMM DD YYYY optional(HH:MM) \n '
                '( For example: $addhw CSC510 HW2 SEP 25 2024 17:02 )')
        print(error)

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: deleteReminder(self, ctx, hwName: str)
    #    Description: Delete a reminder using Classname and Homework name
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    - hwName: name of the homework
    #    Outputs: returns either an error stating a reason for failure or
    #          returns a success message indicating that the reminder has been deleted
    # -----------------------------------------------------------------------------------------------------------------

    @commands.command(name="deletereminder", pass_context=True,
                      help="delete a specific reminder using a homework name using "
                      "$deletereminder HW_NAME ex. $deletereminder HW2 ")
    async def deleteReminder(self, ctx, hwName: str):
        reminders_deleted = db.query(
            'SELECT homework, due_date FROM reminders WHERE guild_id = %s AND homework = %s',
            (ctx.guild.id, hwName)
        )
        db.query(
            'DELETE FROM reminders WHERE guild_id = %s AND homework = %s',
            (ctx.guild.id, hwName)
        )

        for homework, due_date in reminders_deleted:
            due = due_date.strftime("%Y-%m-%d %H:%M:%S")
            await ctx.send(f"Following reminder has been deleted: "
                f"Homework Name: {homework}, Due Date: {due}")

    @deleteReminder.error
    async def deleteReminder_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                'To use the deletereminder command, do: $deletereminder HW_NAME \n '
                '( For example: $deletereminder HW2 )')
        print(error)

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: changeduedate(self, ctx, classid: str, hwid: str, *, date: str)
    #    Description: Update the 'Due date' for a homework by providing the classname and homewwork name
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    - hwid: name of the homework
    #    - date: due date of the assignment
    #    Outputs: returns either an error stating a reason for failure or
    #          returns a success message indicating that the reminder has been updated
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(name="changeduedate", pass_context=True,
                      help="update the assignment date. $changeduedate CLASSNAME HW_NAME MMM DD YYYY optional(HH:MM) "
                      "ex. $changeduedate CSC510 HW2 SEP 25 2024 17:02 ")
    async def changeduedate(self, ctx, hwid: str, *, date: str):
        author = ctx.message.author
        try:
            duedate = datetime.strptime(date, '%b %d %Y %H:%M')
        except ValueError:
            try:
                duedate = datetime.strptime(date, '%b %d %Y')
            except ValueError:
                await ctx.send("Due date could not be parsed")
                return

        # future = (time.time() + (duedate - datetime.today()).total_seconds())
        updated_reminders = db.query(
            'SELECT due_date FROM reminders WHERE guild_id = %s AND homework = %s',
            (ctx.guild.id, hwid)
        )
        db.query(
            'UPDATE reminders SET author_id = %s, due_date = %s WHERE guild_id = %s AND homework = %s',
            (author.id, duedate, ctx.guild.id, hwid)
        )
        for due_date in updated_reminders:
            await ctx.send(f"{hwid} has been updated with following date: {due_date}")

    @changeduedate.error
    async def changeduedate_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                'To use the changeduedate command, do: $changeduedate CLASSNAME HW_NAME MMM DD YYYY optional(HH:MM) \n'
                ' ( For example: $changeduedate CSC510 HW2 SEP 25 2024 17:02 )')
        print(error)

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: duethisweek(self, ctx)
    #    Description: Displays all the homeworks that are due this week along with their due date
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    Outputs: returns either an error stating a reason for failure
    #             or returns a list of all the assignments that are due this week
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(name="duethisweek", pass_context=True,
                      help="check all the homeworks that are due this week $duethisweek")
    async def duethisweek(self, ctx):
        if ctx.guild is None:
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

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: duetoday(self, ctx)
    #    Description: Displays all the homeworks that are due today
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    # Outputs: returns either an error stating a reason for failure or
    #          returns a list of all the assignments that are due on the day the command is run
    # -----------------------------------------------------------------------------------------------------------------
    @commands.command(name="duetoday", pass_context=True, help="check all the homeworks that are due today $duetoday")
    async def duetoday(self, ctx):
        if ctx.guild is None:
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

    # ---------------------------------------------------------------------------------
    #    Function: listreminders(self, ctx)
    #    Description: Print out all the reminders
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    Outputs: returns either an error stating a reason for failure or
    #             returns a list of all the assignments
    # ---------------------------------------------------------------------------------
    @commands.command(name="listreminders", pass_context=True, help="lists all reminders")
    async def listreminders(self, ctx):
        author = ctx.message.author
        if ctx.guild is None:
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

    # ---------------------------------------------------------------------------------
    #    Function: clearallreminders(self, ctx)
    #    Description: Delete all the reminders
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    Outputs: returns either an error stating a reason for failure or
    #             returns a success message stating that reminders have been deleted
    # ---------------------------------------------------------------------------------

    @commands.command(name="clearreminders", pass_context=True, help="deletes all reminders")
    async def clearallreminders(self, ctx):
        if ctx.guild is None:
            db.query('DELETE FROM reminders WHERE author_id = %s', (ctx.author.id,))
            await ctx.send("All your reminders have been cleared.")
        else:
            await ctx.message.delete()
            await ctx.author.send( "That command is DM only. Try DMing me." )

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

    # -----------------------------------------------------------------------------------------------------
    #    Function: delete_old_reminders(self)
    #    Description: asynchronously keeps on tracking the database for expired reminders and cleans them.
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    # -----------------------------------------------------------------------------------------------------
    async def delete_old_reminders(self):
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
