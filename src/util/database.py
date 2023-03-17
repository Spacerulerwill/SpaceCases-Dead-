from os import environ
import pymongo
import certifi
from src.scripts.csgostash_scraper import NO_PRICE_FOUND
from pymongo.collection import Collection
from timeit import default_timer as timer
from datetime import timedelta
from src.util.constants import ONE_WEEK

user_data: Collection # user data - mongodb
trade_requests:Collection # trade requests - mongodb
guild_data:Collection # guild data - mongodb
skin_data_collection:Collection # skin data - mongodb

mongo_client:pymongo.MongoClient

leaderboard = [] # user leaderboard
rooms = {}
wordle_games = {}
skin_data = {}
skin_data_hl = {} # SKIN DATA for higher lower game - does not include knives, glov
containers = {}
word_list = []

# update the leaderboard
def get_leaderboard():
  global leaderboard

  start = timer()
  all_users_data = user_data.find({}).batch_size(4)

  leaderboard = sorted([(user_data["_id"], sum([skin_data["skins"][item["name"]]["price"] for item in user_data["inventory"]])) for user_data in all_users_data], key=lambda x: x[1], reverse=True)
  end = timer()

  print(f"Generated leaderboard in {timedelta(seconds=end-start)}")

# setup database and data
def init_collections():

  global user_data, trade_requests, skin_data_collection, mongo_client, guild_data, word_list

  #try read mongodb database password from database_pass.txt, if fails read from environment variable
  try:
      #read local bot_info
      f = open("database_pass.txt", "r")
      PASS = f.read()
  except FileNotFoundError:
      #read password from environment variable
      PASS = environ["MONGO_DB_PASS"]

  #setup mongodb database
  mongo_url = f"mongodb+srv://admin:{PASS}@csgo-case-bot.odtd2un.mongodb.net/?retryWrites=true&w=majority"
  mongo_client = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

  print("Connected to MongoDB database!")

  # load the csgo bot database
  db = mongo_client['csgo-case-bot']

  # load collections
  user_data = db["user-data"]
  trade_requests = db["trade-requests"]
  guild_data = db["guild-data"]
  skin_data_collection = db["skin-data"]

  trade_requests.create_index([("send-timestamp", pymongo.ASCENDING )], expireAfterSeconds=ONE_WEEK)

  print("Loaded collections")

def load_data():

  global containers, skin_data, skin_data_hl, word_list

  # load container data
  containers = skin_data_collection.find_one({"_id": "container-data"})

  # load skin data
  skin_data = skin_data_collection.find_one({"_id": "skin-data"})
  
  # skin data for higher lower gamae
  skin_data_hl = {key: value for key, value in skin_data["skins"].items() if value["type"] not in ["Gloves", "Knife"] or value["price"] == NO_PRICE_FOUND}

  # word list
  with open("res/wordlist.txt") as f:
    word_list = f.read().splitlines()

  print("Loaded data")