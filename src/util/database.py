from os import environ
import json
import pymongo
import certifi

skin_data = {}
containers = {} # item containers
user_data = {} # user data

# setup database and data
def init():

  global skin_data, containers, user_data

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
  mongo = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

  #load the csgo bot database
  db = mongo['csgo-case-bot']

  #user data collection
  user_data = db["user-data"]

  print("Connected to MongoDB database!")

  # load container data
  with open('res/containers.json', encoding="utf-8") as f:
    containers = json.load(f)

  # load skin data
  with open('res/skin_data.json', encoding="utf-8") as f:
    skin_data = json.load(f)
