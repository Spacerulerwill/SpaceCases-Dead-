from tkinter import filedialog
from src.scripts.collect_skin_api_data import get_api_data, add_skin_prices, add_api_static_data
from src.scripts.csgostash_scraper import get_csgostash_static_data
from threading import Thread
import time
import pymongo
import certifi
from os import environ
import datetime
import json

api_data = {}
skin_prices = {} # all prices
skin_static_data = {} # skin images, rarity colors, rarities
csgostash_static_data = {} # skin min max floats, is stattrak, is souvenir

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

  global skin_static_data, api_data

    #try read mongodb database password from database_pass.txt, if fails read from environment variable
  try:
      #read local bot_info
      f = open("database_pass.txt", "r")
      PASS = f.read()
  except:
      #read password from environment variable
      PASS = environ["MONGO_DB_PASS"]

  # collect skin static data and start price data fetch loop
  api_data = get_api_data()
  Thread(target=update_price_data_loop).start()
  add_skin_prices(skin_prices, api_data)
  add_api_static_data(skin_static_data, api_data)

  #setup mongodb database
  mongo_url = f"mongodb+srv://admin:{PASS}@csgo-case-bot.y4kcpx1.mongodb.net/?retryWrites=true&w=majority"
  mongo = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

  #load the csgo bot database
  db = mongo['csgo-case-bot']

  #skin data collection
  csgostash_static_data_collection = db["skin-data"]

  #insert csgostash_static_data if document doesn't exist
  if csgostash_static_data_collection.find({"_id": "csgostash_static_data"}) == None:
    with open('res/csgostash_static_data.json') as f:
      file_data = json.load(f)
      csgostash_static_data_collection.insert_one(file_data)

  csgostash_static_data = csgostash_static_data_collection.find_one({"_id": "csgostash_static_data"})