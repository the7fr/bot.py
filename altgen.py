import random
import discord
from discord.ext import commands
from discord import app_commands
import json

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

free_items_list = []

premium_items_list = []

letter_items_list = []

def load_generated_items():
    try:
        with open("generated_items.json", "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_generated_items(items):
    with open("generated_items.json", "w") as file:
        json.dump(list(items), file)

def load_items():
    try:
        with open("free_items.json", "r") as file:
            free_items_list = json.load(file)
        with open("premium_items.json", "r") as file:
            premium_items_list = json.load(file)
        with open("letter_items.json", "r") as file:
            letter_items_list = json.load(file)
        return free_items_list, premium_items_list, letter_items_list
    except (FileNotFoundError, json.JSONDecodeError):
        return [], [], []

def save_items():
    with open("free_items.json", "w") as file:
        json.dump(free_items_list, file)
    with open("premium_items.json", "w") as file:
        json.dump(premium_items_list, file)
    with open("letter_items.json", "w") as file:
        json.dump(letter_items_list, file)

generated_items = load_generated_items()
free_items_list, premium_items_list, letter_items_list = load_items()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()

@bot.hybrid_command(name="generate", description="Generate a Roblox account")
@app_commands.describe(type="Select the type of account to generate")
async def generate(ctx: commands.Context, type: str):
    if type == "free":
        items_list = free_items_list
    elif type == "premium":
        if any(role.name == "Premium" for role in ctx.author.roles): 
            items_list = premium_items_list
        else:
            await ctx.send("You need the premium role to access this option.", ephemeral=True)
            return
    elif type == "letter":
        if any(role.name == "Premium" for role in ctx.author.roles):
            items_list = letter_items_list
        else:
            await ctx.send("You need the premium role to access this option.", ephemeral=True)
            return
    else:
        await ctx.send("Invalid option. Please use `free`, `premium`, or `letter`.", ephemeral=True)
        return

    available_items = [item for item in items_list if item not in generated_items]

    if not available_items:
        await ctx.send("Please wait for us to re-stock.")
        return

    item = random.choice(available_items)
    generated_items.add(item)
    save_generated_items(generated_items)

    embed = discord.Embed(title="Generated Item", description=item, color=discord.Color.blue())
    embed.set_footer(text="NOTE: Some accounts may be taken.")

    try:
        await ctx.author.send(embed=embed)
        await ctx.send("I've sent your account details to your DMs.", ephemeral=True)
    except discord.Forbidden:
        await ctx.send("I couldn't send you a DM. Please ensure your DMs are open and try again.")

@generate.error
async def generate_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Command is on cooldown. Try again in {round(error.retry_after, 1)} seconds.",
            ephemeral=True
        )

@bot.hybrid_command(name="stock", description="Show the number of items in stock")
async def stock(ctx: commands.Context):
    free_items_in_stock = len([item for item in free_items_list if item not in generated_items])
    premium_items_in_stock = len([item for item in premium_items_list if item not in generated_items])
    letter_items_in_stock = len([item for item in letter_items_list if item not in generated_items])

    embed = discord.Embed(
        title="Stock Information",
        description=(
            f"Free items in stock: {free_items_in_stock}\n"
            f"Premium items in stock: {premium_items_in_stock}\n"
            f"Letter items in stock: {letter_items_in_stock}"
        ),
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.hybrid_command(name="addstock", description="Add items to the stock")
@app_commands.describe(item_type="Type of item to add (free, premium, or letter)", items="Comma-separated list of items to add")
async def addstock(ctx: commands.Context, item_type: str, *, items: str):
    if any(role.name == "Owner" for role in ctx.author.roles):  
        item_list = items.split(",")
        item_list = [item.strip() for item in item_list] 

        if item_type == "free":
            initial_count = len(free_items_list)
            free_items_list.extend(item_list)
            new_count = len(free_items_list) - initial_count
        elif item_type == "premium":
            initial_count = len(premium_items_list)
            premium_items_list.extend(item_list)
            new_count = len(premium_items_list) - initial_count
        elif item_type == "letter":
            initial_count = len(letter_items_list)
            letter_items_list.extend(item_list)
            new_count = len(letter_items_list) - initial_count
        else:
            await ctx.send("Invalid type. Please use `free`, `premium`, or `letter`.", ephemeral=True)
            return
            
        save_items()

        await ctx.send(f"{new_count} item(s) added to {item_type} stock.", ephemeral=True)
    else:
        await ctx.send("You do not have the required role to use this command.", ephemeral=True)

@bot.hybrid_command(name="history", description="Show the history of command usage")
async def history(ctx: commands.Context):
    try:
        with open("command_history.json", "r") as file:
            command_history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        command_history = {"generate": []}

    num_users = len(command_history["generate"])
    await ctx.send(f"{num_users} users have run the `/generate` command successfully!")

@bot.hybrid_command(name="showstock", description="Show the current stock of items")
async def showstock(ctx: commands.Context):
    if any(role.name == "Owner" for role in ctx.author.roles):
        free_items_in_stock = [item for item in free_items_list if item not in generated_items]
        premium_items_in_stock = [item for item in premium_items_list if item not in generated_items]
        letter_items_in_stock = [item for item in letter_items_list if item not in generated_items]

        stock_message = (
            "Free Items in Stock:\n" +
            "\n".join(free_items_in_stock) +
            "\n\nPremium Items in Stock:\n" +
            "\n".join(premium_items_in_stock) +
            "\n\nLetter Items in Stock:\n" +
            "\n".join(letter_items_in_stock)
        )

        with open("stock_info.txt", "w") as file:
            file.write(stock_message)

        await ctx.send(
            content="Here's the current stock information:",
            file=discord.File("stock_info.txt"),
            ephemeral=True
        )
    else:
        await ctx.send("You need the 'owner' role to use this command.", ephemeral=True)


@bot.hybrid_command(name="clearstock", description="Clear all items from the specified stock")
@app_commands.describe(item_type="Type of stock to clear (free, premium, or letter)")
async def clearstock(ctx: commands.Context, item_type: str):
    if any(role.name == "Owner" for role in ctx.author.roles):  
        def check(msg):
            return msg.author == ctx.author and msg.content.lower() in ['yes', 'no']

        await ctx.send(f"Are you sure you want to clear the {item_type} stock? Type `yes` to confirm or `no` to cancel.", ephemeral=True)

        try:
            confirmation_msg = await bot.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Confirmation timed out. No changes made.", ephemeral=True)
            return

        if confirmation_msg.content.lower() == 'yes':
            if item_type == "free":
                free_items_list.clear()
                await ctx.send("The free stock has been cleared.", ephemeral=True)
            elif item_type == "premium":
                premium_items_list.clear()
                await ctx.send("The premium stock has been cleared.", ephemeral=True)
            elif item_type == "letter":
                letter_items_list.clear()
                await ctx.send("The letter stock has been cleared.", ephemeral=True)
            else:
                await ctx.send("Invalid type. Please use `free`, `premium`, or `letter`.", ephemeral=True)
                return


            save_items()
        else:
            await ctx.send("Operation cancelled. No changes made.", ephemeral=True)
    else:
        await ctx.send("You do not have the required role to use this command.", ephemeral=True)

import shutil

@bot.hybrid_command(name="backup", description="Create a backup of all item lists")
async def backup(ctx: commands.Context):
    if any(role.name == "Owner" for role in ctx.author.roles): 
        try:
            backup_file_paths = {
                "free_items": "backup_free_items.json",
                "premium_items": "backup_premium_items.json",
                "letter_items": "backup_letter_items.json"
            }

            with open("free_items.json", "r") as file:
                shutil.copyfile("free_items.json", backup_file_paths["free_items"])
            with open("premium_items.json", "r") as file:
                shutil.copyfile("premium_items.json", backup_file_paths["premium_items"])
            with open("letter_items.json", "r") as file:
                shutil.copyfile("letter_items.json", backup_file_paths["letter_items"])

            await ctx.send("Backup completed successfully. All item lists have been saved.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"An error occurred while creating the backup: {e}", ephemeral=True)
    else:
        await ctx.send("You do not have the required role to use this command.", ephemeral=True)

try:
    with open("removal_counts.json", "r") as file:
        removal_counts = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    removal_counts = {}

def save_removal_counts():
    with open("removal_counts.json", "w") as file:
        json.dump(removal_counts, file)



try:
    with open("removal_counts.json", "r") as file:
        removal_counts = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    removal_counts = {}

def save_removal_counts():
    with open("removal_counts.json", "w") as file:
        json.dump(removal_counts, file)


try:
    with open("removal_counts.json", "r") as file:
        removal_counts = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    removal_counts = {}

def save_removal_counts():
    with open("removal_counts.json", "w") as file:
        json.dump(removal_counts, file)

@bot.hybrid_command(name="remove", description="Remove an item from the stock")
@app_commands.describe(item_type="Type of item to remove (free, premium, letter)", item="The item to remove")
async def remove(ctx: commands.Context, item_type: str, *, item: str):
    if any(role.name == "Owner" for role in ctx.author.roles):
        item_list = []

        if item_type == "free":
            item_list = free_items_list
        elif item_type == "premium":
            item_list = premium_items_list
        elif item_type == "letter":
            item_list = letter_items_list
        else:
            await ctx.send("Invalid type. Please use `free`, `premium`, or `letter`.", ephemeral=True)
            return

        if item in item_list:
            item_list.remove(item)

            if item not in removal_counts:
                removal_counts[item] = 0
            removal_counts[item] += 1
            save_removal_counts()

            if item_type == "free":
                save_free_items()
            elif item_type == "premium":
                save_premium_items()
            elif item_type == "letter":
                save_letter_items()

            await ctx.send(f"Item '{item}' has been removed {removal_counts[item]} times from {item_type} stock.", ephemeral=True)
        else:
            await ctx.send(f"Item '{item}' not found in {item_type} stock.", ephemeral=True)
    else:
        await ctx.send("You do not have the required role to use this command.", ephemeral=True)




TOKEN = 'BOT_TOKEN_HERE'
bot.run(TOKEN)
