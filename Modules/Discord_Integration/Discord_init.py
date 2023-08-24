import discord
from discord import app_commands
from discord.ext import commands
from discord_token import Token
import Modules.MACD_Analyzer.MACD_Analyzer_old as Macd
import Modules.RSI_Analyzer.RSI_Analyzer_old as Rsi
import Modules.Stochastic_Analyzer.Stochastic_Analyzer_old as Stct
import Modules.Tensorflow_Analyzer.Tensorflow_Analyzer as Tf
import Modules.ADX_Analyzer.ADX_Analyzer as Adx
import Modules.Prophet_Analyzer.Prophet_Analyzer as Prpht
import Modules.Get_Coins_Data.get_coins as GTCoin

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="코인로딩")
async def coin_load(interaction: discord.Interaction, yes_or_no: str):
    await
@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is a slash command!")
@bot.tree.command(name="say")
@app_commands.describe(thing_to_say = "What should I say?")
async def say(interaction: discord.Interaction, thing_to_say: str):
    await interaction.response.send_message(f"{interaction.user.name} said: '{thing_to_say}'")
bot.run(Token)