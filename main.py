import discord
from discord.ext import commands, tasks
import random
import asyncio
import datetime
import discord.ui
from discord.ui import Button, View, Select
import os
import aiohttp
import platform 
import time
import platform
import os
import json
import requests
import aiofiles
import words
import colorama
from colorama import Back, Fore, Style


ROBLOX_API_URL = "https://inventory.roblox.com/v1"
GAMEPASS_ID = 852404961
SUGGESTION_CHANNEL_ID = 1261077890603155516
CONFESSION_CHANNEL_ID = 1261079827952308305
JOIN_CHANNEL_ID =  1262089977739612273
VOUCH_CHANNEL_ID = 1261194067455512616 
AUTOROLE_ID = 1241177374754734101
BUYERROLE_ID = 1241417968621981818
SPECIAL_USER_ID = 1116500847313027145
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1261080153292017764/TGH1HVeXxYjSxE1wRg0oEHWzeZ5s36UXLBoJ9v1rK7FAFxakQD6lU7HQZ0mzx8B6O0p6"

intents = discord.Intents.all()
intents.reactions = True
intents.typing = True 

bot = commands.Bot(command_prefix="/", intents=intents)
bot.warnings = {}
bot.sniped_messages = {}

statuses = ["discord.gg/yon", "BEST SCRIPT OUT!", "BUY NOW!"]

def is_ticket_channel(channel):
    return channel.name.startswith('ticket-')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        bot.warnings[guild.id] = {}
        
        async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
            pass

        async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
            lines = await file.readlines()

            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                reason = " ".join(data[2:]).strip("\n")

                try:
                    bot.warnings[guild.id][member_id][0] += 1
                    bot.warnings[guild.id][member_id][1].append((admin_id, reason))

                except KeyError:
                    bot.warnings[guild.id][member_id] = [1, [(admin_id, reason)]] 
    print(f'Logged in as {bot.user}')
    cycle_status.start()
    synced = await bot.tree.sync()
    prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Style.BRIGHT)
    print(prfx + " Logged in as " + Fore.YELLOW + bot.user.name)
    print(prfx + " Bot ID " + Fore.YELLOW + str(bot.user.id))
    print(prfx + " Discord Version " + Fore.YELLOW + discord.__version__)
    print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()))
    print(prfx + " Command(s) Synced " + Fore.YELLOW + str({len(synced)}))
    print(prfx + " Successfully Changed Bots Activity's To " + Fore.YELLOW + " 'discord.gg/yon', 'BEST SCRIPT OUT!', 'BUY NOW!'")

@bot.event
async def on_message_delete(message):
    bot.sniped_messages[message.guild.id] = (message.content, message.author, message.channel.name, message.created_at)

@bot.hybrid_command(name="closeticket", description="This closes a ticket")
async def closeticket(ctx):
    if is_ticket_channel(ctx.channel):
        if ctx.author.guild_permissions.manage_messages:
            message = await ctx.send("React with ❌ to close this ticket.")
            await message.add_reaction('❌')
        else:
            await ctx.send('You do not have permission to close this ticket.')
    else:
        await ctx.send('This command can only be used in a ticket channel.')

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id or str(payload.emoji) != '❌':
        return
    
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    
    if is_ticket_channel(channel):
        await message.delete()
        await channel.delete()
    else:
        await channel.send("This is not a ticket channel.")

@bot.event
async def on_guild_join(guild):
   bot.warnings[guild.id] = {}

@bot.event
async def on_member_join(member):
    role = member.guild.get_role(AUTOROLE_ID)
    if role:
        await member.add_roles(role)
        print(f"Assigned role {role.name} to {member.name}")

@bot.event
async def on_member_join(member):
    joinchannel = bot.get_channel(JOIN_CHANNEL_ID)
    if joinchannel:
        embed = discord.Embed(title="User Joined The Server!", description="", color=0xFFFFF)
        embed.add_field(name=f"The user {member.name} has joined the server!!!", value="")
        embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
        await joinchannel.send(embed=embed)

@tasks.loop(seconds=10)
async def cycle_status():
    await bot.change_presence(activity=discord.Game(name=statuses[cycle_status.current_loop % len(statuses)]))

async def ticketcallback(interaction):
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name="Staff Team")
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True),
        role: discord.PermissionOverwrite(view_channel=True)
    }

    select = Select(options=[
        discord.SelectOption(label="Buy Ticket", value="01", emoji="📩", description="This will open a buyer ticket"),
        discord.SelectOption(label="Help Ticket", value="02", emoji="📩", description="This will open a ticket for general support")
    ])
    
    async def my_callback(interaction):
        if select.values[0] == "01":
            category = discord.utils.get(guild.categories, name="Buyer Tickets")
            channel = await guild.create_text_channel(f"ticket-{interaction.user.name} (Buyer)", category=category, overwrites=overwrites)
            await interaction.response.send_message(f"Created Ticket - <#{channel.id}>", ephemeral=True)
            await channel.send(f"Hello {interaction.user.mention}! A Staff Member Will Be Here Shortly To Assist You. \n <@&1260297889507446785>")
        elif select.values[0] == "02":
            category = discord.utils.get(guild.categories, name="Support Tickets")
            channel = await guild.create_text_channel(f"ticket-{interaction.user.name} (Support)", category=category, overwrites=overwrites)
            await interaction.response.send_message(f"Created Ticket - <#{channel.id}>", ephemeral=True)
            await channel.send(f"Hello {interaction.user.mention}! A Staff Member Will Be Here Shortly To Assist You. \n <@&1260297889507446785>")
    select.callback = my_callback
    view = View(timeout=None)
    view.add_item(select)
    await interaction.response.send_message("Select a ticket option below", view=view, ephemeral=True)

@bot.hybrid_command(name="createticket", description="This creates a ticket")
async def ticket(ctx):
    button = Button(label="Create Ticket", style=discord.ButtonStyle.red)  
    button.callback = ticketcallback
    view = View(timeout=None)
    view.add_item(button)
    await ctx.send("Open a ticket below", view=view)

def is_ticket_channel(channel):
    return channel.name.startswith('ticket-')

@bot.hybrid_command(description="Syncs all the commands to the bot")
async def sync(ctx: commands.Context):
    await bot.tree.sync()
    await ctx.send("Commands have been synced successfully.")

@bot.hybrid_command(description="Suggest game ideas / suggestions in general")
async def suggest(ctx: commands.Context, *, suggestion: str):
    suggestion_channel = bot.get_channel(SUGGESTION_CHANNEL_ID)
    if suggestion_channel:
        embed = discord.Embed(title="New Suggestion", description=suggestion, color=discord.Color.blurple())
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.set_footer(text=f"User ID: {ctx.author.id}")
        await suggestion_channel.send(embed=embed)
        await ctx.send("Your suggestion has been submitted successfully!")
    else:
        await ctx.send("Could not find the suggestion channel.")

@bot.hybrid_command(name='ban', description='This bans a user from the server.')
@commands.has_any_role("Administrator", "Owner") 
@commands.cooldown(1, 3, commands.BucketType.user)
async def ban(ctx, member:discord.Member, *, reason):
   if reason == None:
       reason = "This user was banned by " + ctx.message.author.name
   await member.ban()
   embed = discord.Embed(title=f"**Banned**", description=f"This user was banned.", color=0xFFFFFF)
   embed.add_field(name=f"**User**", value=f"{member.mention}")
   embed.add_field(name="**Reason**, ", value=f"{reason}")
   await ctx.send(embed=embed)
   banlogs = bot.get_channel(1261749716044087406)
   embed = discord.Embed(title=f"**Banned**", description=f"This user was banned.", color=0xFFFFFF)
   embed.add_field(name="**Reason**", value=f"{reason}")
   embed.add_field(name="**User**", value=f"{member.name}")
   embed.add_field(name="**Moderator**", value=f"{ctx.message.author.mention}")
   await banlogs.send(embed=embed)

@bot.hybrid_command(name='unban', description='This unbans a user from the server.')
@commands.has_any_role("Manager", "Administrator") 
async def unban(ctx, user: discord.User):
   guild = ctx.guild
   await guild.unban(user=user)
   embed = discord.Embed(title=f"**Unbanned**", description=f"This user was unbanned.", color=0xFFFFFF)
   embed.add_field(name="**User**", value=f"{user.mention}")
   await ctx.send(embed=embed)
   unbanlogs = bot.get_channel(1261749716044087406)
   embed = discord.Embed(title=f"**Unbanned**", description=f"This user was unbanned.", color=0xFFFFFF)
   embed.add_field(name="**User**", value=f"{user.name}")
   embed.add_field(name="**Moderator**", value=f"{ctx.message.author.mention}")
   await unbanlogs.send(embed=embed)

@bot.hybrid_command(name='kick', description='This kicks a user from the server.')
@commands.has_any_role("Manager", "Administrator", "Staff") 
@commands.cooldown(1, 3, commands.BucketType.user)
async def kick(ctx, member:discord.Member, *, reason):
   await member.kick()
   embed = discord.Embed(title=f"**Kicked**", description="This user was Kicked.", color=0xFFFFFF)
   embed.add_field(name="**Kicked**", value=f"{member.mention}")
   embed.add_field(name="**Reason**", value=f"{reason}")
   await ctx.send(embed=embed)
   kicklogs = bot.get_channel(1261749716044087406)
   embeds = discord.Embed(title=f"**Kicked**", description="This user was Kicked.", color=0xFFFFFF)
   embeds.add_field(name="**Reason**", value=f"{reason}")
   embeds.add_field(name="**User**", value=f"{member.name}")
   embeds.add_field(name="**Moderator**", value=f"{ctx.message.author.mention}")
   await kicklogs.send(embed=embed)

@bot.hybrid_command(name='mute', description='This mutes a user in the server.')
@commands.has_any_role("Staff Team") 
async def mute(ctx, member: discord.Member, timelimit, *, reason):
   if "s" in timelimit:
       gettime = timelimit.strip("s")
       if int(gettime) > 2419000:
           await ctx.send("Discord only lets you mute 28d max.")
       else:
           newttime = datetime.timedelta(seconds=int(gettime))
           await member.edit(timed_out_until=discord.utils.utcnow() + newttime)
           embed = discord.Embed(title=f"**Muted**", color=0xFFFFFF)
           embed.add_field(name="**User**", value=f"{member.mention}")
           embed.add_field(name=f"**Time**", value=f"{timelimit}")
           embed.add_field(name=f"**Reason**", value=f"{reason}")
           await ctx.send(embed=embed)
           mutelogs = bot.get_channel(1261749716044087406)
           embed = discord.Embed(title=f"**Muted**", color=0xFFFFFF)
           embed.add_field(name="**User**", value=f"{member.name}")
           embed.add_field(name=f"**Time**", value=f"{timelimit}")
           embed.add_field(name=f"**Reason**", value=f"{reason}")
           embed.add_field(name=f"**Moderator**", value=f"{ctx.message.author.mention}")
           await mutelogs.send(embed=embed)
   elif "m" in timelimit:
       gettime = timelimit.strip("m")
       if int(gettime) > 40320:
           await ctx.send("Discord only lets you mute 28d max.")
       else:
           newttime = datetime.timedelta(minutes=int(gettime))
           await member.edit(timed_out_until=discord.utils.utcnow() + newttime)
           embed = discord.Embed(title=f"**Muted**", color=0xFFFFFF)
           embed.add_field(name="**User**", value=f"{member.mention}")
           embed.add_field(name=f"**Time**", value=f"{timelimit}")
           embed.add_field(name=f"**Reason**", value=f"{reason}")
           await ctx.send(embed=embed)
           mutelogs = bot.get_channel(1261749716044087406)
           embed = discord.Embed(title=f"**Muted**", color=0xFFFFFF)
           embed.add_field(name="**User**", value=f"{member.name}")
           embed.add_field(name=f"**Time**", value=f"{timelimit}")
           embed.add_field(name=f"**Reason**", value=f"{reason}")
           embed.add_field(name=f"**Moderator**", value=f"{ctx.message.author.mention}")
           await mutelogs.send(embed=embed)
   elif "h" in timelimit:
       gettime = timelimit.strip("h")
       if int(gettime) > 672:
           await ctx.send("Discord only lets you mute 28d max.")
       else:
           newttime = datetime.timedelta(hours=int(gettime))
           await member.edit(timed_out_until=discord.utils.utcnow() + newttime)
           embed = discord.Embed(title=f"**Muted**", color=0xFFFFFF)
           embed.add_field(name="**User**", value=f"{member.mention}")
           embed.add_field(name=f"**Time**", value=f"{timelimit}")
           embed.add_field(name=f"**Reason**", value=f"{reason}")
           await ctx.send(embed=embed)
           mutelogs = bot.get_channel(1261749716044087406)
           embed = discord.Embed(title=f"**Muted**", color=0xFFFFFF)
           embed.add_field(name="**User**", value=f"{member.name}")
           embed.add_field(name=f"**Time**", value=f"{timelimit}")
           embed.add_field(name=f"**Reason**", value=f"{reason}")
           embed.add_field(name=f"**Moderator**", value=f"{ctx.message.author.mention}")
           await mutelogs.send(embed=embed)
   elif "d" in timelimit:
       gettime = timelimit.strip("d")
       if int(gettime) > 28:
           await ctx.send("Discord only lets you mute 28d max.")
       else:
           newttime = datetime.timedelta(days=int(gettime))
           await member.edit(timed_out_until=discord.utils.utcnow() + newttime)
           embed = discord.Embed(title=f"**Muted**", color=0xFFFFFF)
           embed.add_field(name="**User**", value=f"{member.mention}")
           embed.add_field(name=f"**Time**", value=f"{timelimit}")
           embed.add_field(name=f"**Reason**", value=f"{reason}")
           await ctx.send(embed=embed)
           mutelogs = bot.get_channel(1261749716044087406)
           embed = discord.Embed(title=f"**Muted**", color=0xFFFFFF)
           embed.add_field(name="**User**", value=f"{member.name}")
           embed.add_field(name=f"**Time**", value=f"{timelimit}")
           embed.add_field(name=f"**Reason**", value=f"{reason}")
           embed.add_field(name=f"**Moderator**", value=f"{ctx.message.author.mention}")
           await mutelogs.send(embed=embed)

@bot.hybrid_command(name='unmute', description='This unmutes a user in the server.')
@commands.has_any_role("Staff Team") 
async def unmute(ctx, member:discord.Member):
   await member.edit(timed_out_until=None)
   embed = discord.Embed(title="**Unmuted**", description="This user was Unmuted", color=0xFFFFFF)
   embed.add_field(name="**Unmuted**", value=f"{member.mention}")
   await ctx.send(embed=embed)
   unmutelogs = bot.get_channel(1261749716044087406)
   embed = discord.Embed(title="**Unmuted**", description="This user was Unmuted", color=0xFFFFFF)
   embed.add_field(name="**User**", value=f"{member.name}")
   await unmutelogs.send(embed=embed)
   
@bot.hybrid_command(name="purge", description="This deletes the amout of messages a user does.")
@commands.has_any_role("Staff Team")
@commands.cooldown(1, 5, commands.BucketType.user)
async def purge(ctx, count: int):
   await ctx.channel.purge(limit=count + 1)
   embed = discord.Embed(title="Notification", description="", color=0xd4a5af)
   embed.add_field(name="Successfully Purged!", value=f"{count} Message(s) Have Been Purged")
   await ctx.send(embed=embed)
   logs = bot.get_channel(1261749716044087406)
   embed = discord.Embed(title="Purge Logged", description="", color=0xd4a5af)
   embed.add_field(name="", value=f"{ctx.author.mention} Has Purged {count} Message(s) From {ctx.channel.mention}", inline=False)
   await logs.send(embed=embed)
   
@bot.hybrid_command(name="warn", description="This warns a member in the server")
@commands.has_any_role("Staff Team") 
async def warn(ctx, member: discord.Member=None, *, reason=None):
   if member is None:
      embed = discord.Embed(title="Error", description="The provided member could not be found or you forgot to provide one.", color=0xd4a5af)
      return await ctx.send(embed=embed)
   
   if reason is None:
      embed = discord.Embed(title="Error", description="Please provide a reason for warning this user", color=0xd4a5af)
      return await ctx.send(embed=embed)

   try:
      first_warning = False
      bot.warnings[ctx.guild.id][member.id][0] += 1
      bot.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))

   except KeyError:
      first_warning = True
      bot.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]

   count = bot.warnings[ctx.guild.id][member.id][0]

   async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{member.id} {ctx.author.id} {reason}\n")

   embed = discord.Embed(title="User Warned:", description=f"{member.mention} now has {count} {'warning' if first_warning else ' warnings'}.", color=0xd4a5af)
   embed.add_field(name="Reason:", value=f"'{reason}.'")
   await ctx.send(embed=embed)
   embed = discord.Embed(title="User Warned:", description="A User Was Warned")
   embed.add_field(name="Moderator:", value=f"{ctx.author.name}")
   embed.add_field(name="User Warned:", value=f"{member.name}")
   embed.add_field(name="Reason:", value=f"{reason}")

@bot.hybrid_command(name="warnings", description="This shows the amount of warnings a user has")
async def warning(ctx, member: discord.Member=None):
    if member is None:
        embed = discord.Embed(title="Error", description="The provided member could not be found or you forgot to provide one", color=0xfff)
        return await ctx.send(embed=embed)
      
    embed = discord.Embed(title=f"These are the warnings for {member.name}", description="", color=0xd4a5af)
    try:
        i = 1
        for admin_id, reason in bot.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"**Warning {i}.** Warning Given By: {admin.name}. For the reason of: *'{reason}'*. \n"
            i += 1

        await ctx.send(embed=embed)

    except KeyError:
        embed = discord.Embed(title="Error:", description="This user has no warnings")
        await ctx.send(embed=embed)

purchased_users = []

@bot.hybrid_command(name="purchase", description="Add a username to the purchase list")
@commands.has_any_role("Staff Team")
async def purchase(ctx, member: discord.Member, username: str = None):
    if username is None:
        role = member.guild.get_role(BUYERROLE_ID)
        await member.add_roles(role)
        embed = discord.Embed(title=f"Added role to {member.name}", description="", color=0xff0000)
        await ctx.send(embed=embed)
        return
     
    elif username in purchased_users:
        embed = discord.Embed(title="Purchase Status", description=f"{username} has already bought.", color=0xfffff)
        await ctx.send(embed=embed)
    else:
        role = member.guild.get_role(BUYERROLE_ID)
        await member.add_roles(role)
        purchased_users.append(username)
        embed = discord.Embed(title="Purchase Confirmation", description=f"{username} has been added to the purchase list, and was given the buyer role.", color=0xfffff)
        await ctx.send(embed=embed)


@bot.hybrid_command(description="checks if they have the gamepass")
async def robux(ctx: commands.Context, roblox_user_id: int):
    owned_item_url = f"https://inventory.roblox.com/v1/users/{roblox_user_id}/items/GamePass/{GAMEPASS_ID}/is-owned"

    try:
        response = requests.get(owned_item_url)
        response.raise_for_status()

        body = response.json()

        if body:
            gamepass_link = f"https://www.roblox.com/users/{roblox_user_id}/inventory#!/game-passes"
            await ctx.send(f"This person: {roblox_user_id} owns the gamepass with ID {GAMEPASS_ID}. Please verify [here]({gamepass_link}).")
        else:
            await ctx.send(f"This person {roblox_user_id} tried to scam us with a fake gamepass of the id: {GAMEPASS_ID}.")

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if "private inventory" in error_message.lower():
            await ctx.send(f"The inventory for user with ID {roblox_user_id} is private. Please change it to public.")
        else:
            await ctx.send(f"Error fetching gamepass ownership data: {error_message}")

@bot.hybrid_command(description="grabs a users roblox id from their user to use the /robux cmd") 
async def grab(ctx: commands.Context, *, username: str):
    retries = 3
    for attempt in range(retries):
        try:
            user_search_url = "https://users.roblox.com/v1/usernames/users"
            response = requests.post(user_search_url, json={"usernames": [username], "excludeBannedUsers": False})
            response.raise_for_status()
            users = response.json().get("data", [])

            if users:
                roblox_user_id = users[0]["id"]
                await ctx.send(f"Id for the user: '{username}' is {roblox_user_id}.")
            else:
                await ctx.send(f"User '{username}' not found on Roblox.")
            return

        except requests.exceptions.RequestException as e:
            await ctx.send(f"Error fetching Roblox user ID: {str(e)}")
            return
        except KeyError:
            await ctx.send(f"User '{username}' not found on Roblox.")
            return
        except Exception as e:
            if attempt < retries - 1:
                await ctx.send(f"Error: {str(e)}. Retrying in {2 ** attempt} seconds...")
                await asyncio.sleep(2 ** attempt)
            else:
                await ctx.send(f"Error: {str(e)}")
            continue
        break
    else:
        await ctx.send("Failed to fetch Roblox user ID after retries.")

@bot.hybrid_command(description="Shows the avaliable payment methods")
async def payment_methods(ctx: commands.Context):
    embed = discord.Embed(title="Payment Methods", color=discord.Color.blurple())
    embed.add_field(name="--< Robux >--", value="Buy this gamepass [here](https://www.roblox.com/game-pass/852404961/250) and send your Roblox username/id", inline=False)
    embed.add_field(name="--< BloxFlip >--", value="You will send 250 robux to either of the following users. GOOSEISCUUL, or pilotsights.")
    embed.add_field(name="--< CreditCard/Bank Payment >--", value="Buy the product [here](https://buy.stripe.com/4gw3fPevAaC54F2bIK)", inline=False)
    embed.add_field(name="--< PayPal >--", value="Send $3 to [paypal.me/drxzzy0](https://paypal.me/drxzzy0)", inline=False)
    embed.add_field(name="--< CashApp >--", value="Send $3 to [cash.app/$dorozcsh2](https://cash.app/$dorozcsh2) and send a web receipt once sent", inline=False)
    embed.add_field(name="--< Server Boosts >--", value="2 server boosts = lifetime\n1 server boost = 1 month", inline=False)
    embed.add_field(name="--< Nitro >--", value="2 = lifetime\n1 = 1 month", inline=False)
    embed.add_field(name="--< Crypto >--", value="send $5 LXnFhksmBUHZxkKCbQENpf9EtVAtutMHRs (LTC)", inline=False)
    embed.add_field(name="--< Video Whitelisting >--", value="Make a popular video and get whitelisted for a month (contact for details)", inline=False)
    await ctx.send(embed=embed)

@bot.hybrid_command(description="Nuke the server!")
async def nuke(ctx: commands.Context):
    await ctx.send("You really thought this would work?", ephemeral=True)

@bot.hybrid_command(description="Confess something wild")
async def confess(ctx: commands.Context, *, confession: str):
    confession_channel = bot.get_channel(CONFESSION_CHANNEL_ID)
    if confession_channel:
        try:
            embed = discord.Embed(title="New Confession", description=confession, color=discord.Color.dark_gray())
            embed.set_footer(text="Anonymous Confession")
            await confession_channel.send(embed=embed)

            # Send to webhook
            webhook_data = {
                "username": "Confession Bot",
                "embeds": [{
                    "title": "New Confession",
                    "description": confession,
                    "color": discord.Color.dark_gray().value,
                    "footer": {
                        "text": f"User ID: {ctx.author.id}"
                    },
                    "author": {
                        "name": ctx.author.display_name,
                        "icon_url": ctx.author.display_avatar.url
                    }
                }]
            }
            response = requests.post(WEBHOOK_URL, json=webhook_data)
            response.raise_for_status()

            await ctx.send("Your confession has been sent anonymously!", ephemeral=True)
        except discord.errors.Forbidden:
            await ctx.send("I do not have permission to send messages in the confession channel.", ephemeral=True)
        except requests.exceptions.RequestException as e:
            await ctx.send(f"Failed to send to webhook: {str(e)}", ephemeral=True)
    else:
        await ctx.send("Could not find the confession channel.", ephemeral=True)

@bot.hybrid_command(name='cat', description='Generates a random picture of a cat')
async def cat(ctx):
   async with aiohttp.ClientSession() as session:
    catapi = f'https://api.thecatapi.com/v1/images/search?api-key=live_nPTMsseqZRibPBlXjvENiFni3mbANYSrRUmvUMFfihwH17kM1duBqvizftpSXPeg'
    async with session.get(catapi) as resp:
     results = await resp.json()
     embed = discord.Embed(title="Cat Picture Generated", description="Here is a random generated cat image!", color=0xd4a5af)
     embed.set_image(url=f"{results[0]['url']}")
     await ctx.reply(embed=embed)
     
@bot.hybrid_command(name="dog", description='Generates a random picture of a dog')
async def dog(ctx):
 async with aiohttp.ClientSession() as session:
       dogapi = 'https://dog.ceo/api/breeds/image/random'
       async with session.get(dogapi) as resp:
           results = await resp.json()
           embed = discord.Embed(title="Dog Picture Generated", description="Here is a random generated dog image!", color=0xd4a5af)
           embed.set_image(url=results['message'])
           embed.timestamp = datetime.datetime.utcnow()
           await ctx.send(embed=embed)

filtered_words = words.words

@bot.event
async def on_message(msg):
    for word in filtered_words:
       if word in msg.content:
          await msg.delete()
          embed = discord.Embed(title='Message Blocked', description=f'{msg.author.mention}, Please refrain from using that language', color=0xd4a5af)
          await msg.channel.send(embed=embed)
    await bot.process_commands(msg) 

@bot.hybrid_command(name='dicksize', description="Tell's how big someones dick is")
async def dicksize(ctx):
    if ctx.author.id == SPECIAL_USER_ID:
        percentage = 13
    else:
        percentage = random.randint(1, 13)
    
    embed = discord.Embed(title="How big is someones dick?", description=f"{ctx.author.display_name}'s dick is {percentage}in's", color=0xd4a5af)
    await ctx.send(embed=embed)
   
@bot.hybrid_command(name='niggarate', description="Tell's how black someone is")
async def nigga(ctx):
    if ctx.author.id == SPECIAL_USER_ID:
        percentage = 0
    else:
        percentage = random.randint(1, 100)
    
    embed = discord.Embed(title="How black is someone?", description=f"{ctx.author.display_name} is {percentage}% black", color=0xd4a5af)
    await ctx.send(embed=embed)

@bot.hybrid_command(name='gay', description="Tell's how gay someone is")
async def gay(ctx):
    if ctx.author.id == SPECIAL_USER_ID:
        percentage = 100
    else:
        percentage = random.randint(1, 100)
    
    embed = discord.Embed(title="How gay is someone?", description=f"{ctx.author.display_name} is {percentage}% gay", color=0xd4a5af)
    await ctx.send(embed=embed)
   
@bot.hybrid_command(name="serverinfo", description="This shows the server's information.")
async def serverinfo(ctx):
 embed = discord.Embed(title=f"Server Info For {ctx.guild.name}", description="List Of Server Stats", color=0xFFFFFF)
 embed.add_field(name="Server Name:", value=ctx.guild.name)
 embed.add_field(name="Server ID:", value=ctx.guild.id)
 embed.add_field(name="Server Owner:", value=f"{ctx.guild.owner}#{ctx.guild.owner.discriminator}")
 embed.add_field(name="Server Members:", value=ctx.guild.member_count)
 embed.add_field(name="Server Roles:", value=len(ctx.guild.roles))
 embed.add_field(name="Servers Channels:", value=len(ctx.guild.channels))
 embed.add_field(name="Servers Booster Count:", value=ctx.guild.premium_subscription_count)
 embed.add_field(name="Servers Booster Tier:", value=ctx.guild.premium_tier)
 embed.add_field(name="Booster Role:", value=ctx.guild.premium_subscriber_role)
 embed.add_field(name="Server Creation Date:", value=ctx.guild.created_at.__format__("%A, %D, %B, %Y, @ %H:%M:%S"))
 embed.set_thumbnail(url=ctx.guild.icon)
 embed.set_footer(text=f"Command Executed By {ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar)
 embed.timestamp = datetime.datetime.utcnow()
 await ctx.send(embed=embed)
   
@bot.hybrid_command(name="membercount", description="This shows how many members are in the server.")
async def membercount(ctx):
 embed = discord.Embed(title="Members", description=ctx.guild.member_count, color=0xd4a5af)
 embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
 embed.timestamp = datetime.datetime.utcnow()
 await ctx.send(embed=embed)
 
@bot.hybrid_command(name="8ball", description="Ask a question it will respond with an answer")
async def coinflip(ctx, question):
 with open("eightballresponses.txt", "r") as f:
   random_coinflip_responses = f.readlines()
   coinfresponse = random.choice(random_coinflip_responses)
   embed = discord.Embed(title="Notification", description="", color=0xd4a5af)
   embed.add_field(name=f"{ctx.author.name}#{ctx.author.discriminator} Did the 8ball", value=f"His question was '{question}'", inline=False)
   embed.add_field(name=f"The results are **{coinfresponse}**", value="")
   embed.timestamp = datetime.datetime.utcnow()
 await ctx.send(embed=embed)
 
@bot.hybrid_command(name="ping", description="Shows the latency of the bot.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def ping(ctx):
   if round(bot.latency * 1000) <= 50:
       embed=discord.Embed(title="PING", description=f":ping_pong: Pong! The ping is **{round(bot.latency *1000)}** milliseconds!", color=0xd4a5af)
   elif round(bot.latency * 1000) <= 100:
       embed=discord.Embed(title="PING", description=f":ping_pong: Pong! The ping is **{round(bot.latency *1000)}** milliseconds!", color=0xd4a5af)
   elif round(bot.latency * 1000) <= 200:
       embed=discord.Embed(title="PING", description=f":ping_pong: Pong! The ping is **{round(bot.latency *1000)}** milliseconds!", color=0xd4a5af)
   else:
       embed=discord.Embed(title="PING", description=f":ping_pong: Pong! The ping is **{round(bot.latency *1000)}** milliseconds!", color=0xd4a5af)
   await ctx.send(embed=embed)



@bot.hybrid_command(description="Shows the current features for ff2")
async def features(ctx: commands.Context):
    embed = discord.Embed(title="Game Features", color=discord.Color.blurple())
    embed.add_field(name="--< FF2 >--", value="QB Aimbot\nMagnets\nJumpPower\nAngle Enhancer", inline=False)
    await ctx.send(embed=embed, ephemeral=True)
    
@bot.hybrid_command(name="announce", description="Makes an announcement in the server")
@commands.has_any_role("Co-Owner", "Owner")
async def announce(ctx, *, announcement_title, announcement_message):
    embed = discord.Embed(title=f"{announcement_title}", description="", color=0xFFFFFF)
    embed.add_field(name="", value=f"{announcement_message}")
    await ctx.send(embed=embed)
    await ctx.send("Announcement sent.", ephemeral=True)    

@bot.hybrid_command(description="Check out yon's youtube channel!")
async def youtube(ctx: commands.Context):
    await ctx.send("Check out our YouTube channel: https://www.youtube.com/channel/UCOufVw6T4Fml0pvOlNIovYw")

@bot.hybrid_command(name="joke", description="Get a random joke!")
async def joke(ctx: commands.Context):
    try:
        response = requests.get("https://icanhazdadjoke.com/api")
        if response.status_code == 200:
            joke_data = response.json()
            joke_text = f'{joke_data["setup"]}\n\n{joke_data["punchline"]}'
            await ctx.send(joke_text)
        else:
            await ctx.send("Couldnt find a joke, try again later")
    except Exception as e:
        await ctx.send(f'An error occured: {str(e)}')

@bot.hybrid_command(name="vouch", description="Send a vouch message")
async def vouch(ctx, vouch_user: discord.User,*, vouch_message: str):
    vouch_channel = bot.get_channel(VOUCH_CHANNEL_ID)
    if vouch_channel is None:
        await ctx.send("Vouch chanel not found.")
        return
    else:
        embed = discord.Embed(title="New Vouch!", description=f"{ctx.user.name} has vouched!", color=0xfffff)
        embed.add_field(name="Message", value=vouch_message, inline=False)
        embed.set_footer(text=f"Vouch from {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.guild.icon)
        embed.timestamp = datetime.datetime.utcnow()
        await vouch_channel.send(embed=embed)
        await ctx.send(f"Vouch was made for {vouch_user.mention}")

@bot.hybrid_command(name="weather", description="This shows the local weather for the selected city.")
@commands.cooldown(1, 3, commands.BucketType.user)
async def weather(ctx: commands.Context, *, city):
 url = "http://api.weatherapi.com/v1/current.json"
 params = {
   "key": "5f8d3ebc36d94eb2bbf234556232009",
   "q": city
 }

 async with aiohttp.ClientSession() as session:
   async with session.get(url, params=params) as res:
     data = await res.json()

     location = data["location"]["name"]
     temp_c = data["current"]["temp_c"]
     temp_f = data["current"]["temp_f"]
     humidity = data["current"]["humidity"]
     wind_kph = data["current"]["wind_kph"]
     wind_mph = data["current"]["wind_mph"]
     feelslike_c = data["current"]["feelslike_c"]
     feelslike_f = data["current"]["feelslike_f"]
     last_updated = data["current"]["last_updated"]
     condition = data["current"]["condition"]["text"]
     image_url = "http:" + data["current"]["condition"]["icon"]

     embed = discord.Embed(title=f"Weather for {location}", description=f"The condition in `{location}` is `{condition}`", color=0xd4a5af)
     embed.add_field(name="Temerature", value=f"C: {temp_c} | F: {temp_f}")
     embed.add_field(name="Humidity", value=f"{humidity}")
     embed.add_field(name="Wind Speeds", value=f"KPH: {wind_kph} | MPH: {wind_mph}")
     embed.add_field(name="Feels Like", value=f"C: {feelslike_c} | F: {feelslike_f}")
     embed.add_field(name="Last Updated", value=f"{last_updated}")
     embed.set_thumbnail(url=image_url)
     embed.timestamp = datetime.datetime.utcnow()
     await ctx.send(embed=embed)

@bot.hybrid_command(name="whois", description="This shows information about the selected user.")
@commands.cooldown(1, 5, commands.BucketType.user)
async def whois(ctx, member: discord.Member):
 embed = discord.Embed(title=f"{member.name}#{member.discriminator}", description=f"ID: {member.id}", color=0xd4a5af)
 embed.add_field(name="Joined Discord", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
 embed.add_field(name = "Roles", value=", ".join([role.mention for role in member.roles]), inline=False)
 embed.add_field(name = "Badges", value=", ".join([badge.name for badge in member.public_flags.all()]), inline=False)
 embed.add_field(name="Activity", value=member.activity)
 embed.set_thumbnail(url=member.avatar.url)
 embed.timestamp = datetime.datetime.utcnow()
 await ctx.send(embed=embed)

@bot.hybrid_command(name="information", description="Shows basic information about the bot.")
@commands.cooldown(1, 3, commands.BucketType.user)
async def inforamtion(ctx):
   embed = discord.Embed(title=f"Information <:bleh:1261578566890688602> <:emoji_37:1261893729283739699>", description="This bot was coded by ServerFurry and .nebula.7, using discord.py", color=0xd4a5af)
   embed.set_author(name="angri bot, developed by Server Furry, and .nebula.7", icon_url=ctx.guild.icon)
   await ctx.send(embed=embed)

@bot.event
async def on_message_delete(message):
   embed = discord.Embed(title="Message Deleted", description=f"{message.author.name} deleted a message", color=0xd4a5af)
   embed.add_field(name=f"Message Content", value=f"{message.content}")
   embed.timestamp = datetime.datetime.utcnow()
   channel = bot.get_channel(1261749716044087406)
   await channel.send(embed=embed)

@bot.event
async def on_message_edit(message_before, message_after):
   embed = discord.Embed(title="Message Edited", description=f"{message_before.author.name} edited a message.", color=0xd4a5af)
   embed.add_field(name=f"Message Before:", value=f"{message_before.content}", inline=False)
   embed.add_field(name=f"Message After:", value=f"{message_after.content}", inline=False)
   embed.timestamp = datetime.datetime.utcnow()
   channel = bot.get_channel(1261749716044087406)
   await channel.send(embed=embed)

@bot.hybrid_command(name='role', description="Add's a role to a user")
@commands.has_any_role("Administrator", "Co-Owner", "Owner")
@commands.cooldown(1, 5, commands.BucketType.user)
async def role(ctx, member:discord.Member, *, role:discord.Role = None):
   await member.add_roles(role)
   embed = discord.Embed(title="Added Role(s)", description=f"Added the role '{role} to {member.name}")
   await ctx.send(embed=embed)
   logs = bot.get_channel()
   embed = discord.Embed(title="Added Role(s)", description="")
   embed.add_field(name=f"Role Added To:", value=f"{member}")
   embed.add_field(name=f"Role Added:", value=f"{role}")
   embed.add_field(name=f"Moderator:", value=f"{ctx.message.author}")
   await logs.send(embed=embed)

@bot.hybrid_command(name='removerole', description="Removes a role from a user")
@commands.has_any_role("Administrator", "Co-Owner", "Owner")
@commands.cooldown(1, 5, commands.BucketType.user)
async def role(ctx, member:discord.Member, *, role:discord.Role = None):
   await member.remove_roles(role)
   embed = discord.Embed(title="Removed Role(s)", description=f"Removed the role '{role} from {member.name}")
   await ctx.send(embed=embed)
   logs = bot.get_channel(1196896083020873798)
   embed = discord.Embed(title="Removed Role(s)", description="")
   embed.add_field(name=f"Role Removed From:", value=f"{member}")
   embed.add_field(name=f"Role Removed:", value=f"{role}")
   embed.add_field(name=f"Moderator:", value=f"{ctx.message.author}")
   await logs.send(embed=embed)

@bot.hybrid_command(name="guessnumber", description="Pick a number 1-10.")
async def guessnumber(ctx, your_guess):
   choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
   botchoice = random.choice(choices)
   if your_guess == botchoice:
       await ctx.send("You got it!")
       await ctx.send("https://tenor.com/view/yes-gif-26077231")
   else:
       await ctx.send("Wrong 😭. Try again!")

@bot.event
async def on_command_error(ctx, error):
 if isinstance(error, commands.MissingRequiredArgument):
   embed = discord.Embed(title="Error", description="Error: Missing Arguments", color=0xFFFFFF)
   embed.add_field(name="Make sure you have provided all arguments.", value="")
   embed.timestamp = datetime.datetime.utcnow()
   await ctx.send(embed=embed)
 elif isinstance(error, commands.BotMissingPermissions):
   embed = discord.Embed(title="Error", description="Error: Bot Missing Permissions", color=0xFFFFFF)
   embed.add_field(name="Make sure you have all the needed permissions to run this command.", value="")
   embed.timestamp = datetime.datetime.utcnow()
   await ctx.send(embed=embed)
 elif isinstance(error, commands.MissingAnyRole):
   embed = discord.Embed(title="Error", description="Error: User Missing Roles", color=0xFFFFFF)
   embed.add_field(name="Make sure you have all the required roles to run this command.", value="")
   embed.timestamp = datetime.datetime.utcnow()
   await ctx.send(embed=embed)
 elif isinstance(error, commands.BotMissingAnyRole):
   embed = discord.Embed(title="Error", description="Error: Bot Missing Roles", color=0xFFFFFF)
   embed.add_field(name="Make sure the bot has all the required roles to run this command.", value="")
   embed.timestamp = datetime.datetime.utcnow()
   await ctx.send(embed=embed)
 elif isinstance(error, commands.CommandOnCooldown):
   embed = discord.Embed(title="Cooldown", description=f"You are on cooldown! Retry after **{round(error.retry_after, 2)}** seconds.", color=0xFFFFFF)
   embed.timestamp = datetime.datetime.utcnow()
   await ctx.send(embed=embed)

bot.run('')
