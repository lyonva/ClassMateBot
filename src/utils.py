def get_guild_name_by_id(ctx, guild_id):
    serv = [g.name for g in ctx.bot.guilds if g.id == guild_id]
    return serv[0] if len(serv) == 1 else ""


def get_all_guild_names_by_id(ctx, guild_id_list):
    return [get_guild_name_by_id(ctx, id) for id in guild_id_list]


def get_all_ids_by_user(ctx):
    aid = ctx.author.id
    all_guilds = ctx.bot.guilds
    return [g.id for g in all_guilds if g.get_member(aid) is not None]


async def chooseGuild(self, ctx):
    """
    Function: chooseGuild
    Description: finds all servers user is a part of through a DM message with the bot
    Inputs:
        - ctx: context of the command
    Outputs:
        - guild_list: List of all guild id's the user is associated with
        - msg: int representation of the number the user entered
    """
    msg = ""
    guild_list = []
    if ctx.guild == None:

        # Checks if a message is received from a user and not the bot
        def check(m):
            return m.content is not None and m.channel == ctx.channel and m.author == ctx.author

        guilds = get_all_ids_by_user(ctx)
        valid_answer = False

        # Loop that asks a user to choose a server they are in that has the bot
        while valid_answer == False:
            msg = ""
            guild_list_string = "Choose a server (enter the number): \n"
            current = 1
            guild_list = []
            if guilds == []:
                await ctx.author.send("You are not in any servers")
            else:
                for guild in guilds:
                    guild_list.append(guild)
                    guild_list_string += f"{current}. {get_guild_name_by_id( ctx, guild )}\n"  # Prints each server
                    current += 1
                await ctx.author.send(guild_list_string)
                msg = await self.bot.wait_for("message", check=check)  # Waits for user input
                try:
                    msg = int(msg.content)
                    valid_answer = True
                except Exception as e:
                    print(e)
                    await ctx.author.send("You have entered an invalid option\n")
    return [guild_list, msg]
