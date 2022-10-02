import pymongo
import certifi
from os import environ
from scripts.collect_skin_prices import get_skin_prices
from scripts.collect_skin_static_data import get_skin_static_data
from threading import Thread
import time

#try read mongodb database password from database_pass.txt, if fails read from environment variable
try:
    #read local bot_info
    f = open("database_pass.txt", "r")
    PASS = f.read()
except:
    #read password from environment variable
    PASS = environ["MONGO_DB_PASS"]

skin_prices = None
skin_static_data = None

# skin price loop - every hour update price data
def update_price_data_loop():
    global skin_prices
    while True:
        skin_prices = get_skin_prices()
        time.sleep(10)

# setup database and data
def init_database():
    global skin_static_data

    # collect skin data and start price data fetch loop
    Thread(target=update_price_data_loop).start()
    skin_static_data = get_skin_static_data()

    #setup mongodb database
    mongo_url = f"mongodb+srv://admin:{PASS}@csgo-case-bot.y4kcpx1.mongodb.net/?retryWrites=true&w=majority"
    mongo = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

    #load the csgo bot database
    db = mongo['csgo-case-bot']