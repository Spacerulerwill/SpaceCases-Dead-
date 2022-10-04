from src.scripts.collect_skin_prices import get_api_data, add_skin_prices, add_skin_images
from src.scripts.collect_skin_static_data import get_skin_static_data
from threading import Thread
import time
import pymongo
import certifi
from os import environ
import datetime

api_data = {}
skin_prices = {}
skin_static_data = {}

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
  add_skin_images(skin_static_data, api_data)

  #setup mongodb database
  mongo_url = f"mongodb+srv://admin:{PASS}@csgo-case-bot.y4kcpx1.mongodb.net/?retryWrites=true&w=majority"
  mongo = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

  #load the csgo bot database
  db = mongo['csgo-case-bot']