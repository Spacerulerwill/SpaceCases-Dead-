import pymongo
import subprocess
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid
from src.scripts.csgostash_scraper import csgostash_scrape
from src.scripts.container_scraper import scrape_containers


def try_create_collection(db: Database, name: str) -> Collection:
    try:
        collection = db.create_collection(name)
    except CollectionInvalid:
        db.drop_collection(name)
        collection = db.create_collection(name)

    print(f"Created {name}")
    return collection


def script_run():
    bot_token = input("Enter bot token: ")

    with open("bot_token.txt", "w+") as f:
        f.write(bot_token)

    try:
        subprocess.run("md \data\db", check=True, shell=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        if (
            e.stderr.decode("utf-8")
            != "A subdirectory or file \\data\\db already exists.\r\n"
        ):
            print(
                "Could not run command md \data\db. Have you installed MongoDB Community Server?"
            )
            return

    # setup mongodb database
    mongo_url = "mongodb://127.0.0.1:27017"
    mongo_client = pymongo.MongoClient(mongo_url)
    print("Connection successful!")

    mongo_client.drop_database("local")
    mongo_client.drop_database("config")

    # create fake database and collections
    db = mongo_client["csgo-case-bot"]
    guild_data = try_create_collection(db, "guild-data")
    user_data = try_create_collection(db, "user-data")
    trade_requests = try_create_collection(db, "trade-requests")
    skin_data_collection = try_create_collection(db, "skin-data")
    patch_notes = try_create_collection(db, "patch-notes")

    print("Inserting skin data - this may take a while!")

    skin_data = csgostash_scrape()
    skin_data_collection.replace_one({"_id": "skin-data"}, skin_data, upsert=True)

    container_data = scrape_containers()
    skin_data_collection.replace_one(
        {"_id": "container-data"}, container_data, upsert=True
    )
    print("Complete!")


if __name__ == "__main__":
    script_run()
    input("")
