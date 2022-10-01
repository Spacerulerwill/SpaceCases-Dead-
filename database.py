import pymongo
import certifi
from os import environ

#try read mongodb database password from database_pass.txt, if fails read from environment variable
try:
    #read local bot_info
    f = open("database_pass.txt", "r")
    PASS = f.read()
except:
    #read password from heroku
    PASS = environ["MONGO_DB_PASS"]

# collections
def init_database():
    #setup mongodb database
    mongo_url = f"mongodb+srv://admin:{PASS}@csgo-case-bot.qw8aayh.mongodb.net/?retryWrites=true&w=majority"
    mongo = pymongo.MongoClient(mongo_url, tlsCAFile=certifi.where())

    #load the csgo bot database
    db = mongo['csgo-case-bot']