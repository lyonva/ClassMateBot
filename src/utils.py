def get_guild_name_by_id( ctx, guild_id ):
    serv = [ g.name for g in ctx.bot.guilds if g.id == guild_id]
    return serv[0] if len(serv) == 1 else ""

def get_all_guild_names_by_id( ctx, guild_id_list ):
    return [ get_guild_name_by_id( ctx, id ) for id in guild_id_list ]

def get_all_ids_by_user( ctx ):
    aid = ctx.author.id
    all_guilds = ctx.bot.guilds
    return [ g.id for g in all_guilds if g.get_member( aid ) is not None ]

