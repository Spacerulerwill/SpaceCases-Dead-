from os import environ
import pymongo
import json
import certifi
from pymongo.collection import Collection
from timeit import default_timer as timer
from datetime import timedelta

user_data: Collection # user data - mongodb
trade_requests:Collection # trade requests - mongodb
guild_data:Collection # guild data - mongodb

mongo_client:pymongo.MongoClient

leaderboard = [] # user leaderboard
rooms = {}
skin_data = {}
containers = {}

# update the leaderboard
def get_leaderboard():
  global leaderboard

  start = timer()
  all_users_data = user_data.find({}).batch_size(4)

  leaderboard = sorted([(user_data["_id"], sum([skin_data["skins"][item["name"]]["price"] for item in user_data["inventory"]])) for user_data in all_users_data], key=lambda x: x[1], reverse=True)
  end = timer()

  print(f"Generated leaderboard in {timedelta(seconds=end-start)}")

# setup database and data
def init():

  global user_data, trade_requests, mongo_client, skin_data, containers, guild_data

  #try read mongodb database password from database_pass.txt, if fails read from environment variable
  try:
      #read local bot_info
      f = open("database_pass.txt", "r")
      PASS = f.read()
  except:
      #read password from environment variable
      PASS = environ["MONGO_DB_PASS"]

  #setup mongodb database
  mongo_url = f"mongodb+srv://admin:{PASS}@csgo-case-bot.odtd2un.mongodb.net/?retryWrites=true&w=majority"
  mongo_client = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

  print("Connected to MongoDB database!")

  #load the csgo bot database
  db = mongo_client['csgo-case-bot']

  #user data collection
  user_data = db["user-data"]
  trade_requests = db["trade-requests"]
  guild_data = db["guild-data"]

  print("Loaded user data")

  # load container data
  with open('res/containers.json', encoding="utf-8") as f:
    containers = json.load(f)

  # load skin data
  with open('res/skin_data.json', encoding="utf-8") as f:
    skin_data = json.load(f)
