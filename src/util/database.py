from os import environ
import json
import pymongo
import certifi

skin_data = {}
containers = {} # item containers
user_data = {} # user data
user_actions = {} # store what command user is currently using

OPENING_CASE = 0
IN_INVENTORY = 1
UPGRADING_ITEM = 2

#responses for each action when trying to perform a new one
user_action_responses = [
  "You are currently opening a case! Please cancel this command first",
  "You are currently in your inventory! Please close it before using this command",
  "You are currently upgrading a skin! Please cancel this command first"
]

# setup database and data
def init():

  global skin_data, containers, user_data, user_actions

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

  print("Connected to MongoDB database!")

  #load the csgo bot database
  db = mongo['csgo-case-bot']

  #user data collection
  user_data = db["user-data"]

  print("Loaded user data")

  # set user actions all to none for every user 
  for document in user_data.find():
    user_actions[document["_id"]] = None

  print("User commands all set to default value")

  # load container data
  with open('res/containers.json', encoding="utf-8") as f:
    containers = json.load(f)

  # load skin data
  with open('res/skin_data.json', encoding="utf-8") as f:
    skin_data = json.load(f)
