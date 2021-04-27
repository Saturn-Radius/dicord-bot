#octa-bot.py
import os
import asyncio
import discord
import requests
import json
import locale
import time

from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import bot
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = os.getenv('CHANNEL_ID')
BSCSCAN_URL = os.getenv('BSCSCAN_BASE_URL')
POOCOIN_URL = os.getenv('POOCOIN_BASE_URL')
DEXGURU_URL = os.getenv('DEXGURU_BASE_URL')
BURNED_URL = os.getenv('API_BURNED_URL')
CIRCULATION_URL = os.getenv('API_CIRCULATION_URL')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH')

locale.setlocale(locale.LC_ALL, '')
driver = webdriver.Chrome(DRIVER_PATH)

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
  guild = discord.utils.get(bot.guilds, name=GUILD)
  print(f'{bot.user} is connected to the following guild:\n'
    f'{guild.name}(id: {guild.id})')


@bot.command(
  help="Uses this command for getting OCTA price",
  brief="Show Octa Price"
)
async def price(ctx):
  if ctx.channel.id != int(CHANNEL_ID):
    # await ctx.message.delete()
    return

  if ctx.author == bot.user:
    return

  driver.get(DEXGURU_URL + CONTRACT_ADDRESS + '?sort_by=id&sort_by2=address&asc=false&from_num=0&size=15')
  time.sleep(1)
  price = driver.find_element_by_xpath('/html/body/pre').get_attribute('innerText')
  price_value = price.split()
  str_price = json.loads(price_value[0])["priceUSD"]
  result_price = format(str_price, '.10f')
  million_price = float(result_price) * float(1000000)

  driver.get(BSCSCAN_URL+CONTRACT_ADDRESS)
  time.sleep(1)
  bnb_price = driver.find_element_by_xpath('//*[@id="ethPrice"]/div/span').get_attribute('innerText')
  bnb_price_value = bnb_price.split()
  str_bnb_price = bnb_price_value[1][1:]
  octa_bnb = int(float(str_bnb_price) / float(result_price))

  result = ":Octa: $" + str(result_price)  + "\n 1,000,000 Octa = $"+str(million_price)+"\n 1 BNB = " + str(f'{octa_bnb:n}') + " octa"

  await ctx.message.delete()
  await ctx.send(result)


@bot.command(
  help="Uses this command for getting MARKET CAP",
  brief="Show Octa Market CAP"
)
async def mcap(ctx):
  if ctx.channel.id != int(CHANNEL_ID):
    return

  if ctx.author == bot.user:
    return

  driver.get(BSCSCAN_URL + CONTRACT_ADDRESS)
  time.sleep(2)
  marketcap = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_tr_valuepertoken"]/div/div[2]/span/span').get_attribute('innerText')
  market_cap_value = marketcap.split()
  print(market_cap_value[0])
  result = ":chart_with_upwards_trend: Current market cap is `" + market_cap_value[0] +'`'
  await ctx.message.delete()
  await ctx.send(result)


@bot.command(
  help="Uses this command for holders of OCTA",
  brief="Show Octa Holders"
)
async def holders(ctx):
  if ctx.channel.id != int(CHANNEL_ID):
    return

  if ctx.author == bot.user:
    return

  driver.get(BSCSCAN_URL+CONTRACT_ADDRESS)
  time.sleep(1)
  holders = driver.find_element_by_xpath('/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div').get_attribute('innerText')
  holders = holders.split()
  result = ":people_hugging:" + holders[0] + " Octanauts holding!"
  await ctx.message.delete()
  await ctx.send(result)


@bot.command(
  help="Uses this command for amount of OCTA",
  brief="Show Octa Amount"
)
async def supply(ctx):
  if ctx.channel.id != int(CHANNEL_ID):
    return

  if ctx.author == bot.user:
    return

  burnt_response = requests.get(BURNED_URL)
  burnt = burnt_response.json()
  circulation_response = requests.get(CIRCULATION_URL)
  circulation = circulation_response.json()

  if circulation_response.status_code != 200:
    return
  if burnt_response.status_code != 200:
    return

  await ctx.message.delete()
  result = ":arrows_counterclockwise: " + str(f'{circulation:n}') + "  circulating \n" + ":fire: "+str(f'{burnt:n}')+"  burnt"
  await ctx.send(result)


@bot.command(
  help="Uses this command for information of OCTA",
  brief="Show Octa Information"
)
async def info(ctx):
  if ctx.channel.id != int(CHANNEL_ID):
    return

  if ctx.author == bot.user:
    return
  await ctx.message.delete()
  await ctx.send("Information about OCTA")


@bot.command(
  help="Uses this command for instruction of buying OCTA",
  brief="Show how to buy OCTA"
)
async def howtobuy(ctx):
  if ctx.channel.id != int(CHANNEL_ID):
    return

  if ctx.author == bot.user:
    return
  await ctx.message.delete()
  await ctx.send("How to buy OCTA")


bot.run(TOKEN)