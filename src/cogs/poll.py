from discord.ext import commands
import discord

reactions=['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣ ','🔟']

class poll(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # -----------------------------------------------------------------------------------------------------------------
    #    Function: poll(self, ctx)
    #    Description: going through the steps to create a poll in a specific chanel
    #    Inputs:
    #       - ctx: context of the command
    #       - pollText: the text of question of the poll between quotation marks
    #       - options: answers to the poll in one text separated by commas and all are between quotation marks , max number: 10
    #    Outputs:
    #       - a post contains the poll with a reaction to every possible option to make it easy to choose
    # -----------------------------------------------------------------------------------------------------------------
    @commands.has_role('Instructor')
    @commands.command(name='poll', help='post a poll. first write the text of the poll in quotations then a space and then list of options (max: 10) separated by commas. EX: $poll "what is that" "A,B,C"')
    async def createPoll(self, ctx,pollText: str, options: str):
        
        items = options.split(',')
        # check if the poll contains only one option
        if len(items) == 1:

            # send a direct message explaining the issuse
            channel = await ctx.author.create_dm()
            await ctx.message.delete()
            await channel.send('Error: You can not have a poll with only one option to choose')
            return
        
        poll = discord.Embed(title=pollText)
        M=[]
        # For each item add an emoji with the option
        for item, emoji in zip(items,reactions):
            poll.add_field(name=emoji, value=item, inline=False)
            M.append(emoji)

        # set a footer 
        poll.set_footer(text="Votes: |{}".format('.'.join(M)))
        # post the poll
        msg  = await ctx.channel.send(embed=poll)
        # add a reaction to every option to make it fast to choose a one
        for i in range(len(items)):
            await msg.add_reaction(reactions[i])

# -----------------------------------------------------------------------------------------------------------------
    #    Function: createPoll_error(self, ctx, error)
    #    Description: prints error message for poll command
    #    Inputs:
    #       - ctx: context of the command
    #       - error: error message
    #    Outputs:
    #       - Error details
    # -----------------------------------------------------------------------------------------------------------------
    @createPoll.error
    async def createPoll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(
                'To use the poll command, do: $poll "Poll Text" "option1,option2,option3,..." \n '
                '(For example: $poll "what is that" "A,B,C")')
        else:
            await ctx.author.send(error)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(poll(bot))

    @bot.event
    async def on_reaction_add(reaction, user):
        msg=reaction.emoji 
        # check if the reaction is in the allowed reaction of the poll
        if msg not in reactions:
            await reaction.clear()
        
        # The following code is for limiting the number of reactions by one user
        # The code is not working propely 
        '''count = 0
        for u in reaction.message.reactions:
            if user.id == u.message.author.id:
                count += 1
                print(count)
                if count > 1:
                    print('No Way')
                    await reaction.clear()'''


        

            






