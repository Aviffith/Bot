import discord
from discord.ext import commands, tasks
import random
import os

# Enable intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Replace with your actual IDs
CHANNEL_ID = 1354850550985920697
USER_ID = 1177294135313584138

reminder_active = False  # Track if reminders are active

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    
    # Sync commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s) with Discord!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# Water Reminder System
@tasks.loop(minutes=1)
async def water_reminder():
    global reminder_active
    if reminder_active:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"<@{USER_ID}> Don't forget to drink water!")
        else:
            print("⚠️ Channel not found!")
    else:
        print("⚠️ Reminder is not active!")

@bot.tree.command(name="startreminder", description="Start the water reminder")
async def start_reminder(interaction: discord.Interaction):
    global reminder_active
    if not water_reminder.is_running():
        water_reminder.start()
        reminder_active = True
        await interaction.response.send_message("✅ Water reminders have started!", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Water reminders are already running!", ephemeral=True)

@bot.tree.command(name="stopreminder", description="Stop the water reminder")
async def stop_reminder(interaction: discord.Interaction):
    global reminder_active
    if water_reminder.is_running():
        water_reminder.cancel()
        reminder_active = False
        await interaction.response.send_message("❌ Water reminders have been stopped!", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Water reminders are already stopped!", ephemeral=True)

@bot.tree.command(name="remind", description="Manually trigger a water reminder")
async def remind(interaction: discord.Interaction):
    await interaction.response.send_message(f"<@{USER_ID}> Don't forget to drink water! 💧")

# ✅ Clear Messages Command
@bot.command(name="clear", help="Delete a specified number of messages in this channel")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount > 100:
        await ctx.send("⚠️ You can only delete up to 100 messages at a time.")
        return

    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ Deleted {len(deleted) - 1} messages.", delete_after=3)

# ✅ Rock-Paper-Scissors Game
@bot.tree.command(name="rps", description="Play Rock-Paper-Scissors!")
async def rps(interaction: discord.Interaction, choice: str):
    options = {"r": 1, "p": -1, "s": 0}
    reverse_dict = {1: "rock", -1: "paper", 0: "scissor"}
    
    if choice not in options:
        await interaction.response.send_message("⚠️ Invalid choice! Use 'r' for rock, 'p' for paper, or 's' for scissor.", ephemeral=True)
        return

    # User and computer choice
    user_choice = options[choice]
    computer_choice = random.choice([-1, 0, 1])

    # Determine the result
    if user_choice == computer_choice:
        result = "It's a draw!"
    elif (user_choice == 1 and computer_choice == 0) or \
         (user_choice == -1 and computer_choice == 1) or \
         (user_choice == 0 and computer_choice == -1):
        result = "✅ You win!"
    else:
        result = "❌ You lose!"

    await interaction.response.send_message(
        f"You chose **{reverse_dict[user_choice]}**\nComputer chose **{reverse_dict[computer_choice]}**\n**{result}**"
    )

# Run the bot
bot.run(os.getenv("TOKEN"))
