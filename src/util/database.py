from os import environ
import pymongo
from gridfs import GridFS
import certifi
from pymongo.collection import Collection
from timeit import default_timer as timer
from datetime import timedelta
from src.util.constants import ONE_WEEK
from src.scripts.csgostash_scraper import NO_PRICE_FOUND
from src.scripts.csgostash_scraper import csgostash_scrape
from src.scripts.container_scraper import (
    case_scrape,
    souvenir_package_scrape,
    collection_scrape,
    sticker_capsule_scrape,
)
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
skin_data = {}
skin_data_hl = {}  # SKIN DATA for higher lower game - does not include knives, glov
containers = {}  # all containers that are openable
collections = {}
cases_and_collections = {}  # just cases and collections
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
    global containers, collections, cases_and_collections, skin_data, skin_data_hl, word_list

    # load container data
    containers = skin_data_collection.find_one({"_id": "container-data"})

    # load skin data
    skin_data = skin_data_collection.find_one({"_id": "skin-data"})

    # load collection data
    cases_and_collections = skin_data_collection.find_one(
        {"_id": "cases-and-collections-data"}
    )

    # skin data for higher lower gamae
    skin_data_hl = {
        key: value
        for key, value in skin_data["skins"].items()
        if value["item_type"] == "weapon"
        and (
            value["type"] not in ["Gloves", "Knife"] or value["price"] == NO_PRICE_FOUND
        )
    }

    # word list
    with open("res/wordlist.txt") as f:
        word_list = f.read().splitlines()

    print("Loaded data")


def scrape_skin_data(scrape_containers: bool = False):
    global skin_data
    skin_data = csgostash_scrape(scrape_containers)

    skin_data_collection.replace_one({"_id": "skin-data"}, skin_data, upsert=True)


def scrape_container_data():
    global containers, collections, cases_and_collections

    case_data = case_scrape()
    collections = collection_scrape()
    souvenir_data = souvenir_package_scrape(collections)
    sticker_capsule_data = sticker_capsule_scrape()

    containers = {
        "_id": "container-data",
        **case_data,
        **souvenir_data,
        **sticker_capsule_data,
    }
    cases_and_collections = {
        "_id": "cases-and-collections-data",
        **case_data,
        **collections,
    }

    # upload to mongodb
    skin_data_collection.find_one_and_replace(
        {"_id": "container-data"}, containers, upsert=True
    )

    skin_data_collection.find_one_and_replace(
        {"_id": "cases-and-collections-data"}, cases_and_collections, upsert=True
    )
