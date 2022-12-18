from os import environ
import pymongo
import json
import certifi

user_data = {}# user data
trade_requests = {}
skin_data = {}
containers = {}
mongo_client:pymongo.MongoClient

# setup database and data
def init():

  global user_data, trade_requests, mongo_client, skin_data, containers

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

  print("Loaded user data")

  # load container data
  with open('res/containers.json', encoding="utf-8") as f:
    containers = json.load(f)

  # load skin data
  with open('res/skin_data.json', encoding="utf-8") as f:
    skin_data = json.load(f)
