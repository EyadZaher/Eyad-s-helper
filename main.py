import discord
import json 
import random
import asyncio
import os
import pymongo
import datetime
import time 
from pymongo import MongoClient
from discord.enums import Status
from discord.ext import commands
from discord.ext import tasks 
from itertools import cycle
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option  
from discord.role import Role

intents = discord.Intents().default()   
client = commands.Bot(command_prefix='.', intents=intents)
status = cycle(['Status 1', 'Status 2'])
slash = SlashCommand(client, sync_commands=True)       
cluster = MongoClient("mongodb+srv://Eyad:Nahlahome114@warn-command-db.nmb7l.mongodb.net/Eyad?retryWrites=true&w=majority")
database = cluster["Eyad"]
collection = database["warn database"]



@slash.slash(
     name="hello",
     description="Just sends a message",
     guild_ids=[854121191312588880, 767105642405429249, 821101084536733707]
)
async def _hello(ctx:SlashContext):
    await ctx.send("World!")


@slash.slash(
    name="Ping",
    description="Shows the bot's latency",
    guild_ids=[854121191312588880, 767105642405429249, 821101084536733707]
)
async def ping(ctx):
    await ctx.send(f'pong {round(client.latency * 1000)}ms')

options = [
    {
        "name" : "start",
        "description" : "The starting limit of the guess",
        "required" : False,
        "type" : 4
    },
    {
        "name" : "stop",
        "description" : "The stopping limit of the guess",
        "required" : False,
        "type" : 4
    }
]




@slash.slash(
       name = 'Guess',
       description = 'Guesses a number',
       guild_ids = [854121191312588880, 767105642405429249, 821101084536733707]) 
async def guess(ctx: SlashContext , start = 0, stop = 100):
    randomNumber = random.randint(start , stop)   
    await ctx.send(content = f"Your random number is {randomNumber}")



@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit=amount)

def is_it_me(ctx):
    return ctx.author.id == 731997026866298952


@client.command(pass_context=True)
@commands.has_permissions(manage_guild=True)
async def addrole(ctx, member: discord.Member, *, role: discord.Role = None):

    await member.add_roles(role)
    await ctx.send(f'{member} Was Given {role}')

@client.command()
async def members(ctx):
    embedVar = discord.Embed(title=f'There Are {ctx.guild.member_count} Members In This Server', color=0xFF0000)
    await ctx.send(embed=embedVar)

@client.command()
@commands.check(is_it_me)
async def example(ctx):
    await ctx.send(f'Hi im {ctx.author}')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('dang fam invalid command used :thinking:')


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please specify an amount of messages to delete.')

@client.command()
async def ping(ctx):
    await ctx.send(f'pong {round(client.latency * 1000)}ms')

@client.event
async def on_ready():
    
    print('Bot is ready to use')


snipe_message_author = {}
snipe_message_content = {}
    
@client.event
async def on_message_delete(message):
      snipe_message_author[message.channel.id]= message.author  
      snipe_message_content[message.channel.id]= message.content    
      await asyncio.sleep(60)       
      del snipe_message_author[message.channel.id]
      del snipe_message_content[message.channel.id]

@client.command()  
async def snipe(ctx):
    channel= ctx.channel  
    try:
        snipeEmbed = discord.Embed(title=f"Last deleted message in #{channel.name}", description = snipe_message_content[channel.id])
        snipeEmbed.set_footer(text=f"Deleted by {snipe_message_author[channel.id]}")
        await ctx.send(embed = snipeEmbed)   
    except:
        await ctx.send(f"There are no deleted messages in #{channel.name}")



@client.command()
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Set the slowmode delay in this channel to {seconds} seconds!") 

@client.event  
async def on_member_join(member, guild):
    await client.get_channel().send(f"{member.name} has joined {guild.name}")


@client.command()
async def poll(ctx, *, question=None):
    if question == None:
        await ctx.send("Please write a poll!")

    icon_url = ctx.author.avatar_url 

    pollEmbed = discord.Embed(title = "New Poll!", description = f"{question}")

    pollEmbed.set_footer(text = f"Poll given by {ctx.author}", icon_url = ctx.author.avatar_url)

    pollEmbed.timestamp = ctx.message.created_at 

    await ctx.message.delete()

    poll_msg = await ctx.send(embed = pollEmbed)

    await poll_msg.add_reaction("⬆️")
    await poll_msg.add_reaction("⬇️")
        

@client.command()
async def kick(ctx, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'Successfully kicked {member.mention} | reason = {reason} | He was kinda sus tho lol')

@client.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention} | reason = {reason} |Have a nice day haha')

@client.command()
async def unban(ctx, *, member): 
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user  

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f"Unbanned {user.name}#{user.discriminator}")
            return  

def convert(datetime):
    pos = ["s","m","h","d"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600 , "d" : 3600*24}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2


    return val * time_dict[unit] 

@client.command()
async def mute(ctx, member:discord.Member, *, reason=None): 
   role = discord.utils.get(ctx.guild.roles, name="Muted")
   guild = ctx.guild 
   if role not in guild.roles:
       perms = discord.Permissions(send_messages=False, speak=False) 
       await guild.create_role(name="Muted", permissions=perms) 
       await asyncio.sleep(datetime)

       await member.add_roles(role) 
       await ctx.send(f"The member has been muted")
   else:
       await member.add_roles(role) 
       await ctx.send(f"{member} has been muted | reason: {reason}")

@client.command(pass_context=True)
@commands.has_permissions(manage_guild=True)
async def removerole(ctx, member: discord.Member, *, role: discord.Role = None):

    await member.remove_roles(role)
    await ctx.send(f'{member} s {role} was removed')



@client.command()
@commands.has_permissions(manage_nicknames=True)
async def setnick(ctx, member:discord.Member,*,nick=None):
    old_nick = member.display_name

    await member.edit(nick=nick)

    new_nick = member.display_name

    await ctx.send(f'Changed nick from *{old_nick}* to *{new_nick}*')
    
@client.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx,*,reason='None'):
    channel =ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

    embed=discord.Embed(title=f'🔒 Locked',description=f'Reason: {reason}')

    await channel.send(embed=embed)

@client.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx,*,reason='None'):
    channel =ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    embed=discord.Embed(title=f'🔓 Unlocked',description=f'Reason: {reason}')
    await channel.send(embed=embed)


@client.command(case_insensitive=True)
async def unmute(ctx, member: discord.Member, *, reason=None):

    guild = ctx.guild
    muteRole = discord.utils.get(guild.roles, name = "Muted")

    if not muteRole:  
       await ctx.send("The Mute role can't be found! Please check if there is a mute role or if th user has already has it")  
       return
    await member.remove_roles(muteRole, reason=reason)
    await ctx.send(f"{member.mention} has been unmuted in {ctx.guild} | reason: {reason}") 
    await member.send(f"You have been muted in {ctx.guild} | reason: {reason}")

@client.command(aliases=['8ball'])
async def eightball(ctx, *, question):
    responses  = ["It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes - definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful.",
                "Maybe."]
    await ctx.send(f':8ball: Answer: {random.choice(responses)}')

 
#commands
@client.command()
@commands.has_permissions(manage_channels=True)
async def warn(ctx, user:discord.Member=None, *, reason=None):
        id = user.id 
        if collection.count_documents({"memberid":id}) == 0:
            collection.insert_one({"memberid": id,"warns": 0})

        if reason==None:
            return await ctx.send("Please mention a reason!")
        elif user==None:
            return await ctx.send("Please mention a user!")

        warn_count = collection.find_one({"memberid":id})

        count = warn_count["warns"]
        new_count = count + 1 
        ok_count = int(new_count)

        collection.update_one({"memberid":id},{"$set":{"warns": ok_count}})

        await ctx.send(f"Warned {user.mention} for {reason} in {ctx.guild} | They now have {new_count} warnings!")
        await client.get_channel(849033773496401990).send(f"Warned {user.mention} for {reason} in {ctx.guild} | They now have {new_count} warnings!")
@client.command()
async def avatar(ctx, member: discord.Member=None):
    if member == None:
        member = ctx.author
    
    icon_url = member.avatar_url 
 
    avatarEmbed = discord.Embed(title = f"{member.name}\'s Avatar", color = 0xFFA500)
 
    avatarEmbed.set_image(url = f"{icon_url}")
 
    avatarEmbed.timestamp = ctx.message.created_at 
 
    await ctx.send(embed = avatarEmbed)   


@client.event
async def on_member_join(member):
    channel = client.get_channel(836382789229871114)

    em=discord.Embed(
        title=f'Welcome',
        description=f'{member.mention} Joined {member.guild.name}',
        color=discord.Color.random(),
        timestamp=datetime.utcnow()
        ).add_field(
        name=f':hey: Rules',
        value=f'<#821101085062201449>'
        ).add_field(
        name=f':hey: Chat',
        value='<#859853615962783791>'
        ).add_field(
        name=f'Total members',
        value=f'{member.guild.member_count}'
        ).set_footer(text=f'{member.name} just joined')

    await channel.send(embed=em)

@client.command()
@commands.has_permissions(administrator=True)
async def gstart(ctx, time=None, *, prize=None):
    if time == None:
        return await ctx.send("Please include a time!")
    elif prize == None:
        return await ctx.send("Please include a prize!")
    embed = discord.Embed(title='GIVEAWAY!', description=f'{ctx.author.mention} is doing a **GIVEAWAY**!!')
    time_convert = {"s":1, "m":60, "h":3600}
    gawtime = int(time[0] * time_convert[time[-1]])
    embed.add_field(name = "The prize is:", value = f"{prize}")
    embed.set_footer(text=f"Giveaway ends in {time}!")
    embed.set_image(url="https://cdn.discordapp.com/attachments/859813691113340945/859864158136172554/standard.gif")
    gaw_msg = await ctx.send(embed = embed)

    await gaw_msg.add_reaction("🎉")
    await asyncio.sleep(gawtime)

    new_gaw_msg = await ctx.channel.fetch_message(gaw_msg.id)

    users = await new_gaw_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))

    winner = random.choice(users)

    await ctx.send(f"Congrats {winner.mention} on winning {prize}! dm Giveaway managers or mods to claim your prize!")

@client.command()
async def cringe(ctx):

    embed = discord.Embed(
        colour=discord.Colour.blue(),
        title="You posted cringe",
        description="Dont post cringe again please"
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/859813691113340945/859886467722248232/tenor.gif")
    embed.set_footer(text="Bot made by Eyad")

    await ctx.send(embed=embed)



client.run('ODU1ODc3MzQ3MTU1NjQwMzUx.YM435A.msUjlnebc140Jb2bqHqSPJ1-j5c')

