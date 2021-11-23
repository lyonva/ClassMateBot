# Copyright (c) 2021 War-Keeper
import os
import sys

from discord.ext import commands

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import db
# -----------------------------------------------------------
# This File contains commands for voting on projects,
# displaying which groups have signed up for which project
# -----------------------------------------------------------
class Voting(commands.Cog):

    # -----------
    # initialize
    # -----------
    def __init__(self, bot):
        self.bot = bot

    # ----------------------------------------------------------------------------------------------------------
    #    Function: vote(self, ctx, arg2='-1')
    #    Description: "votes" for the given project by adding the users group to it
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    - project_num: the number of the project to vote for with group
    #    Outputs: adds the user to the given project, switching if already in a project
    #             or returns an error if the project is invalid or the user is not in a valid group
    # ----------------------------------------------------------------------------------------------------------
    @commands.command(name='vote', help='Used for voting for Projects, \
    To use the vote command, do: $vote <Num> \n \
    (For example: $vote 0)', pass_context=True)
    async def vote(self, ctx, project_num : int):
        # get the name of the caller
        member_name = ctx.message.author.display_name.upper()

        if project_num < 0 or project_num > 99:
            await ctx.send("A valid project number is 1-99.")
            return

        all_groups = db.query(
            'SELECT group_num FROM group_members'
        )

        flag = False

        for group in all_groups:
            if group[0] == project_num:
                flag = True
                break
        
        if not flag:
            await ctx.send("The entered Project Group does not exist. Please vote for a existing group only.")
            return
    
        group = db.query(
            'SELECT group_num FROM group_members WHERE guild_id = %s AND member_name = %s',
            (ctx.guild.id, member_name)
        )

        # error handle if member is not in a group
        if len(group) == 0:
            await ctx.send("You are not in a group. You must join a group before voting on a project.")
            return

        group = group[0][0]

        num_groups = db.query(
            'SELECT COUNT(*) FROM project_groups WHERE guild_id = %s AND project_num = %s',
            (ctx.guild.id, project_num)
        )[0]

        check_limit = db.query(
            "SELECT count(*) FROM project_limit WHERE guild_id = %s AND author_id = %s",
            (ctx.guild.id,ctx.author.id)
        )[0]

        if  check_limit[0] != 0:

            curr_limit = db.query(
            "SELECT count FROM project_limit WHERE guild_id = %s AND author_id = %s",
            (ctx.guild.id,ctx.author.id)
            )

            # check if project has more than 6 groups voting on it
            if num_groups[0] >= curr_limit[0][0]:
                await ctx.send(f'Projects are limited to {curr_limit[0][0]} groups, please select another project.')
                return

        else:
            # check if project has more than 6 groups voting on it
            if num_groups[0] == 3:
                await ctx.send('Projects are limited to 3 groups by default, please select another project' +
                               ' or contact the instructor to change the limit.')
                return

        voted_for = db.query(
            'SELECT project_num FROM project_groups WHERE guild_id = %s AND group_num = %s',
            (ctx.guild.id, group)
        )

        if voted_for:
            voted_for = voted_for[0][0]
            if voted_for == project_num:
                await ctx.send(f'You already voted for Project {voted_for}')
                return

            db.query(
                'DELETE FROM project_groups WHERE guild_id = %s AND group_num = %s',
                (ctx.guild.id, group)
            )
            await ctx.send(f'Group {group} removed vote for Project {voted_for}')

        # add the group to the project list
        db.query(
            'INSERT INTO project_groups (guild_id, project_num, group_num) VALUES (%s, %s, %s)',
            (ctx.guild.id, project_num, group)
        )
        await ctx.send(f'Group {group} has voted for Project {project_num}!')

    # this handles errors related to the vote command
    @vote.error
    async def vote_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send('To join a project, use the join command, do: $vote <Num> \n'
            '( For example: $vote 0 )')
        print(error)


    # ----------------------------------------------------------------------------------
    #    Function: projects(self, ctx)
    #    Description: prints the list of current projects
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    Outputs: prints the list of current projects
    # ----------------------------------------------------------------------------------
    @commands.command(name='projects', help='print projects with groups assigned to them', pass_context=True)
    # @commands.dm_only()
    async def projects(self, ctx):
        projects = db.query(
            "SELECT project_num, string_agg(group_num::text, ', ') AS group_members "
            "FROM project_groups WHERE guild_id = %s GROUP BY project_num",
            (ctx.guild.id,)
        )

        if len(projects) > 0:
            await ctx.send('\n'.join(f'Project {project_num}: Group(s) {group_members}'
                                     for project_num, group_members in projects))
        else:
            await ctx.send('There are currently no votes for any project numbers.')

    
    '''@commands.command(name='delete', help='print projects with groups assigned to them', pass_context=True)
    # @commands.dm_only()
    async def delete(self, ctx):
        projects = db.query(
            'DELETE FROM project_limit',
            (ctx.guild.id, ctx.author.id) 
        )
        await ctx.send('Deleted successfully.')

    @commands.command(name='display', help='print projects with groups assigned to them', pass_context=True)
    # @commands.dm_only()
    async def display(self, ctx):

        projects = db.query(
            "SELECT count FROM project_limit"
        )

        if len(projects) > 0:
            await ctx.send('\n'.join(f'Project {count}'
                                     for count in projects))
        else:
            await ctx.send('There are currently no votes for any project numbers.')'''

    # ----------------------------------------------------------------------------------------------------------
    #    Function: setlimit(self, ctx, count = '-1')
    #    Description: Sets limit for the number of votes each group can receive for their respective project
    #    Inputs:
    #    - self: used to access parameters passed to the class through the constructor
    #    - ctx: used to access the values passed through the current context
    #    - count: the maximum number of votes a group can receive.
    #    Outputs: sets the limit for the number of votes each group can receive for their respective project
    #             or returns an error if the count is invalid or the user is not in a valid group.
    # ----------------------------------------------------------------------------------------------------------

    @commands.command(name='setlimit', help='Used to set limit for number of votes each project can receive, \
    To use the setlimit command, do: $setlimit <Num> \n \
    (For example: $setlimit 1)', pass_context=True)
    async def setlimit(self, ctx, count : int):

        # get the name of the caller
        member_name = ctx.message.author.display_name.upper()
        author = ctx.message.author
        guild = ctx.guild

        if author != guild.owner:
            await ctx.send("Only the instructor can use this command.")
            return
        
        if count < 0 or count > 40:
            await ctx.send("A valid project limit is 1-40.")
            return

        num = db.query(
            "SELECT count(*) FROM project_limit WHERE guild_id = %s AND author_id = %s",
            (guild.id,author.id)
        )[0]

        if num[0] != 0:

            db.query(
                "UPDATE project_limit SET count = %s WHERE guild_id = %s AND author_id = %s",
                (count,ctx.guild.id,author.id)
            )
            await ctx.send(f'Limit updated to {count}')

        else:

            db.query(
                'INSERT INTO project_limit (guild_id, author_id, count) VALUES (%s, %s, %s)',
                (guild.id, author.id, count)
            )
            await ctx.send(f'The limit has been set to {count}')

    # this handles errors related to the vote command
    @setlimit.error
    async def vote_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            await ctx.send('To set project limit, use the setlimit command, do: $setlimit <Limit> \n'
            '( For example: $setlimit 1 )')
        print(error)

# -----------------------------------------------------------
# add the file to the bot's cog system
# -----------------------------------------------------------
def setup(bot):
    bot.add_cog(Voting(bot))
