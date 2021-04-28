#octa-bot.py
import os
import asyncio
import discord
import requests
import json
import locale
import time

from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.ext.commands import bot
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from datetime import date

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL_ID = os.getenv('CHANNEL_ID')
MARKET_CHANNEL_ID = os.getenv('MARKET_CHANNEL_ID')
BSCSCAN_URL = os.getenv('BSCSCAN_BASE_URL')
BSCSCAN_ADDRESS_URL= os.getenv('BSCSCAN_ADDRESS_URL')
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
  market_match.start()
  print('Starting bot....')


# @bot.event
# async def on_message(message):
#   await bot.process_commands(message)


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

  driver.get(BSCSCAN_ADDRESS_URL+CONTRACT_ADDRESS)
  time.sleep(2)
  token_price = driver.find_element_by_xpath('//*[@id="mCSB_1_container"]/ul/li[2]/a/div[2]/span[2]').get_attribute('innerText')
  token_price_value = token_price.split()
  result_price = token_price_value[0][1:]

  # driver.get(DEXGURU_URL + CONTRACT_ADDRESS + '?sort_by=id&sort_by2=address&asc=false&from_num=0&size=15')
  # time.sleep(1)
  # price = driver.find_element_by_xpath('/html/body/pre').get_attribute('innerText')
  # price_value = price.split()
  # str_price = json.loads(price_value[0])["priceUSD"]
  # result_price = format(str_price, '.10f')
  million_price = float(result_price) * float(1000000)

  driver.get(BSCSCAN_URL+CONTRACT_ADDRESS)
  time.sleep(1)
  bnb_price = driver.find_element_by_xpath('//*[@id="ethPrice"]/div/span').get_attribute('innerText')
  bnb_price_value = bnb_price.split()
  str_bnb_price = bnb_price_value[1][1:]
  octa_bnb = int(float(str_bnb_price) / float(result_price))

  result = ":money_with_wings: $" + str(result_price)  + "\n 1,000,000 Octa = $"+str(million_price)+"\n 1 BNB = " + str(f'{octa_bnb:n}') + " octa"

  # await ctx.message.delete()
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
  # print(market_cap_value[0])
  result = ":chart_with_upwards_trend: Current market cap is `" + market_cap_value[0] +'`'
  # await ctx.message.delete()
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
  # await ctx.message.delete()
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
  burnt_j = burnt_response.json()
  burnt = int(str(burnt_j)[0:15])

  circulation_response = requests.get(CIRCULATION_URL)
  circulation_j = circulation_response.json()
  circulation = int(str(circulation_j)[0:15])

  if circulation_response.status_code != 200:
    return
  if burnt_response.status_code != 200:
    return

  # await ctx.message.delete()
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
  # await ctx.message.delete()
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
  # await ctx.message.delete()
  await ctx.send("How to buy OCTA")


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])


@tasks.loop(minutes=2)
async def market_match():
  market_channel = bot.get_channel(int(MARKET_CHANNEL_ID))

  #Get Price
  driver.get(BSCSCAN_ADDRESS_URL+CONTRACT_ADDRESS)
  time.sleep(2)
  token_price = driver.find_element_by_xpath('//*[@id="mCSB_1_container"]/ul/li[2]/a/div[2]/span[2]').get_attribute('innerText')
  token_price_value = token_price.split()

  #Volume
  driver.get(DEXGURU_URL + CONTRACT_ADDRESS + '?sort_by=id&sort_by2=address&asc=false&from_num=0&size=15')
  time.sleep(1)
  volume = driver.find_element_by_xpath('/html/body/pre').get_attribute('innerText')
  volume_value = volume.split()
  volume_24h = json.loads(volume_value[0])["volume24hUSD"]

  # result_price = format(str_price, '.10f')

  #Total Burned
  burnt_response = requests.get(BURNED_URL)
  burnt_j = burnt_response.json()
  burnt = str(burnt_j)[0:15]

  #holders
  driver.get(BSCSCAN_URL+CONTRACT_ADDRESS)
  time.sleep(1)
  holders = driver.find_element_by_xpath('/html/body/div[1]/main/div[4]/div[1]/div[1]/div/div[2]/div[3]/div/div[2]/div/div').get_attribute('innerText')
  holders = holders.split()

  print("This message is sending on only this channel")

  todays_date = date.today()
  embed_message = discord.Embed(
    title=CONTRACT_ADDRESS,
    description="This bot will automatically post new stats every 2 minutes.",
    url=BSCSCAN_URL+CONTRACT_ADDRESS,
    color=0x00ff00
  )
  embed_message.set_author(name="Octa Price Bot")
  embed_message.set_thumbnail(url="https://images-ext-1.discordapp.net/external/sht-EejpwUqQvdsKk3SuCaR3mVckfwqpp2I2UX3Jsq8/https/octanscrypto.com/wp-content/uploads/2021/03/cropped-Favicon-1024x1024.png?width=494&height=494")
  embed_message.add_field(name=":money_with_wings: Price", value="$"+token_price_value[0][1:], inline=True)
  embed_message.add_field(name=":ice_cube: Volume", value="$"+human_format(volume_24h), inline=True)
  embed_message.add_field(name=":bank: Total Supply", value="1000T", inline=True)
  embed_message.add_field(name=":fire: Total Burned", value=human_format(int(burnt)), inline=True)
  embed_message.add_field(name=":people_hugging: Holders", value=holders[0], inline=True)
  embed_message.set_footer(text="Octa Price Bot - Values based on USD. • {}".format(todays_date))
  await market_channel.send(embed=embed_message)

bot.run(TOKEN)