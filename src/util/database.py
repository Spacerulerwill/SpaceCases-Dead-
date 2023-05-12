from os import environ
import pymongo
from gridfs import GridFS
import certifi
from pymongo.collection import Collection
from timeit import default_timer as timer
from datetime import timedelta
from src.util.constants import ONE_WEEK
from src.scripts.csgo_data_scraper import scrape_game_data
from discord.ext.commands.bot import Bot

# MongoDB collections
user_data: Collection
trade_requests: Collection
guild_data: Collection
leaderboards: Collection
skin_data_collection: Collection
fs: GridFS

mongo_client: pymongo.MongoClient

# Bot data
rooms = {}
wordle_games = {}
item_data  = {}
skin_data_hl = {}  # SKIN DATA for higher lower game - does not include knives, gloves, stickers
containers = {}  # all containers that are openable
word_list = []


def get_leaderboard(bot: Bot):
    """Regenerate the leaderboard"""
    start = timer()
    all_users_data = user_data.find({}).batch_size(4)

    # global leaderboard
    global_ldb = sorted(
        [
            (
                user_data["_id"],
                sum(
                    [
                        skin_data["skins"][item["name"]]["price"]
                        for item in user_data["inventory"]
                    ]
                ),
            )
            for user_data in all_users_data
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    leaderboards.replace_one({"_id": "global"}, {"data": global_ldb}, upsert=True)
    end = timer()
    print(f"Generated global leaderboard in {timedelta(seconds=end-start)}")

    # local server leaderboards
    start = timer()
    for guild in bot.guilds:
        id_list = [member.id for member in guild.members]
        local_leaderboard = [(_id, val) for _id, val in global_ldb if _id in id_list]
        leaderboards.replace_one(
            {"_id": guild.id}, {"data": local_leaderboard}, upsert=True
        )
    end = timer()

    print(f"Generated local leaderboards in {timedelta(seconds=end-start)}")


# setup database and data
def init_collections():
    global user_data, trade_requests, skin_data_collection, mongo_client, leaderboards, guild_data, word_list

    localhost = False
    # try read mongodb database password from database_pass.txt, if fails read from environment variable
    try:
        # read local bot_info
        f = open("database_pass.txt", "r")
        PASS = f.read()
    except FileNotFoundError:
        # read password from environment variable
        try:
            PASS = environ["MONGO_DB_PASS"]
        except:
            # using localhost
            localhost = True

    if localhost:
        try:
            mongo_url = "mongodb://127.0.0.1:27017"
            mongo_client = pymongo.MongoClient(mongo_url)
        except:
            print("Failed to connect to localhost MongoDB")
            return
    else:
        try:
            # setup mongodb database from web server
            mongo_url = f"mongodb+srv://admin:{PASS}@csgo-case-bot.odtd2un.mongodb.net/?retryWrites=true&w=majority"
            mongo_client = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())
        except:
            print("Failed to connect to MongoDB web server")
            return

    print("Connected to MongoDB database!")

    # load the csgo bot database
    db = mongo_client["csgo-case-bot"]
    fs = GridFS(db)

    # load collections
    user_data = db["user-data"]
    trade_requests = db["trade-requests"]
    guild_data = db["guild-data"]
    skin_data_collection = db["skin-data"]
    patch_notes = db["patch-notes"]
    leaderboards = db["leaderboards"]

    # create indexes
    trade_requests.create_index(
        [("send-timestamp", pymongo.ASCENDING)], expireAfterSeconds=ONE_WEEK
    )  # TRADES DELETE AFTER ONE WEEK

    print("Loaded collections")


def load_data():
    global containers, skin_data, skin_data_hl, word_list

    # load container data
    containers = skin_data_collection.find_one({"_id": "container-data"})

    # load skin data
    skin_data = skin_data_collection.find_one({"_id": "skin-data"})

    # skin data for higher lower gamae
    skin_data_hl = {
        key: value
        for key, value in skin_data["skins"].items()
        if value["item_type"] == "weapon"
        and (
            value["type"] not in ["gloves", "knife", "sticker"] or value["price"] == NO_PRICE_FOUND
        )
    }

    # word list
    with open("res/wordlist.txt") as f:
        word_list = f.read().splitlines()

    print("Loaded data")


def refresh_game_data():
    global item_data, containers

    item_data, containers = scrape_game_data()
    skin_data_collection.replace_one({"_id": "item_data"}, item_data, upsert=True)
    skin_data_collection.find_one_and_replace({"_id": "container_data"}, containers, upsert=True)