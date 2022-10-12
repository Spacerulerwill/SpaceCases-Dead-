from src.scripts.collect_skin_api_data import get_api_data, add_skin_prices, add_api_static_data
from src.scripts.csgostash_scraper import get_csgostash_static_data
from threading import Thread
import time
from os import environ
import datetime
import json

api_data = {}
skin_prices = {} # all prices
skin_static_data = {} # skin images, rarity colors, rarities
csgostash_static_data = {} # skin min max floats, is stattrak, is souvenir
containers = {} # item containers

delta_hour = datetime.datetime.now().hour

# skin price loop - every hour update price data
def update_price_data_loop():
  global skin_prices, delta_hour, api_data

  while True:
    now_hour = datetime.datetime.now().hour

    if delta_hour != now_hour:
        api_data = get_api_data()
        add_skin_prices(skin_prices, api_data)

    delta_hour = now_hour
    time.sleep(60) # 60 second

# setup database and data
def init():

  global skin_static_data, api_data, csgostash_static_data, containers
  
  # collect skin static data and start price data fetch loop
  api_data = get_api_data()
  Thread(target=update_price_data_loop).start()
  add_skin_prices(skin_prices, api_data)
  add_api_static_data(skin_static_data, api_data)

  #insert csgostash_static_data if document doesn't exist
  with open('res/csgostash_static_data.json', encoding="utf-8") as f:
    csgostash_static_data = json.load(f)
  with open('res/containers.json', encoding="utf-8") as f:
    containers = json.load(f)
