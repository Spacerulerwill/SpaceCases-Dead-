"""
Copyright (C) 2023 William Redding - All Rights Reserved

Contains all mongoDB collections and leaderboard updating logic

Functions
~~~~~~~~~
* get_leaderboard
* init_collections
* load_data
* refresh_game_data

See end of file for licence details
"""

import os
import logging
import pymongo
from gridfs import GridFS
import certifi
from pymongo.collection import Collection
from timeit import default_timer as timer
from datetime import timedelta
from src.util.constants import ONE_WEEK, NO_PRICE_FOUND
from src.scripts.csgo_data_scraper import scrape_game_data
from discord.ext.commands.bot import Bot

# MongoDB collections
mongo_client: pymongo.MongoClient
fs: GridFS

user_data: Collection
trade_requests: Collection
guild_data: Collection
leaderboards: Collection
game_data: Collection

# Bot data
rooms = {}
wordle_games = {}
item_data = {}
item_data_hl = (
    {}
)  # SKIN DATA for higher lower game - does not include knives, gloves, stickers
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
                        item_data["items"][item["name"]]["price"]
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
    logging.info(f"Generated global leaderboard in {timedelta(seconds=end-start)}")

    # local server leaderboards
    start = timer()
    for guild in bot.guilds:
        id_list = [member.id for member in guild.members]
        local_leaderboard = [(_id, val) for _id, val in global_ldb if _id in id_list]
        leaderboards.replace_one(
            {"_id": guild.id}, {"data": local_leaderboard}, upsert=True
        )
    end = timer()

    logging.info(f"Generated local leaderboards in {timedelta(seconds=end-start)}")


# setup database and data
def init_collections():
    global user_data, trade_requests, patch_notes, game_data, mongo_client, leaderboards, guild_data, word_list

    localhost = False
    try:
        PASS = os.getenv("DATABASE_PASS")
    except:
        # using localhost
        localhost = True

    if localhost:
        try:
            mongo_url = "mongodb://127.0.0.1:27017"
            mongo_client = pymongo.MongoClient(mongo_url)
        except:
            logging.critical("Failed to connect to localhost MongoDB")
            return
    else:
        try:
            # setup mongodb database from web server
            mongo_url = f"mongodb+srv://admin:{PASS}@csgo-case-bot.odtd2un.mongodb.net/?retryWrites=true&w=majority"
            mongo_client = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())
        except:
            logging.critical("Failed to connect to MongoDB web server")
            return

    logging.info("Connected to MongoDB database!")

    # load the csgo bot database
    db = mongo_client["csgo-case-bot"]
    fs = GridFS(db)

    # load collections
    user_data = db["user_data"]
    trade_requests = db["trade_requests"]
    guild_data = db["guild_data"]
    game_data = db["game_data"]
    patch_notes = db["patch_notes"]
    leaderboards = db["leaderboards"]

    # create indexes
    trade_requests.create_index(
        [("send-timestamp", pymongo.ASCENDING)], expireAfterSeconds=ONE_WEEK
    )  # TRADES DELETE AFTER ONE WEEK

    logging.info("Loaded collections")


def load_game_data():
    global containers, item_data, item_data_hl, word_list

    # load container data
    containers = game_data.find_one({"_id": "container_data"}, {"_id": False})

    # load skin data
    item_data = game_data.find_one({"_id": "item_data"}, {"_id": False})

    # skin data for higher lower gamae
    item_data_hl = {
        key: value
        for key, value in item_data["items"].items()
        if value["item_type"] == "weapon"
        and (
            value["type"] not in ["gloves", "knife", "sticker"]
            or value["price"] == NO_PRICE_FOUND
        )
    }

    # word list
    with open("res/wordlist.txt") as f:
        word_list = f.read().splitlines()

    logging.info("Loaded game data")


def refresh_game_data():
    global item_data, containers

    item_data, containers = scrape_game_data()
    game_data.replace_one({"_id": "item_data"}, item_data, upsert=True)
    game_data.find_one_and_replace({"_id": "container_data"}, containers, upsert=True)


"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
