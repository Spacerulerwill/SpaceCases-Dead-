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

"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.
"""