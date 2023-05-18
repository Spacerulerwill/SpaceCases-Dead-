"""
Copyright (C) 2023 William Redding - All Rights Reserved

A build script for setting up a local mongoDB database for development purposes. Please read the setup guide in CONTRIBUTING.md before running

See end of file for licence details
"""

import pymongo
import os
from dotenv import set_key
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid
from src.scripts.csgo_data_scraper import scrape_game_data
from src.util.constants import ONE_WEEK


def try_create_collection(db: Database, name: str) -> Collection:
    try:
        collection = db.create_collection(name)
    except CollectionInvalid:
        db.drop_collection(name)
        collection = db.create_collection(name)

    print(f"Created {name}")
    return collection


def script_run():
    os.system("pip install -r requirements.txt")

    bot_token = input("Enter bot token: ")

    open(".env", "w+").close()
    set_key(".env", "BOT_TOKEN", bot_token)

    # setup mongodb database
    mongo_url = "mongodb://127.0.0.1:27017"
    mongo_client = pymongo.MongoClient(mongo_url)
    print("Connection successful!")

    mongo_client.drop_database("local")
    mongo_client.drop_database("config")

    # create fake database and collections
    db = mongo_client["csgo-case-bot"]
    guild_data = try_create_collection(db, "guild_data")
    user_data = try_create_collection(db, "user_data")
    trade_requests = try_create_collection(db, "trade_requests")
    item_data_collection = try_create_collection(db, "item_data")
    patch_notes = try_create_collection(db, "patch_notes")
    leaderboards = try_create_collection(db, "leaderboards")

    # create indexes
    trade_requests.create_index(
        [("send-timestamp", pymongo.ASCENDING)], expireAfterSeconds=ONE_WEEK
    )  # TRADES DELETE AFTER ONE WEEK

    print("Gathering game data - this may take a while!")

    item_data, container_data = scrape_game_data()
    item_data_collection.replace_one({"_id": "item_data"}, item_data, upsert=True)
    item_data_collection.replace_one(
        {"_id": "container_data"}, container_data, upsert=True
    )
    print("Complete!")


if __name__ == "__main__":
    script_run()
    input("")

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
