from src.util.emojis import *

PREFIX = "cs "
TWELVE_HOURS = 43200
ONE_DAY = 86400
ONE_WEEK = ONE_DAY * 7
KEY_PRICE = 250

DEFAULT_INVENTORY_SIZE = 15
INVENTORY_ELEMS_PER_PAGE = 10
LEADERBOARD_ELEMS_PER_PAGE = 10
MAX_TRADES_PER_PAGE = 10
MAX_THREADS = 30

ROOM_DELETION_TIME = 900

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPRGX/104.0.4480.100"
}

# rarity to color
rarity_color_dict = {
    "consumer": 11584473,
    "industrial": 6199513,
    "milspec": 4942335,
    "restricted": 8931327,
    "classified": 13839590,
    "covert": 15420235,
    "contraband": 14986809,
}

rarity_emoji_dict = {
    "consumer": CONSUMER_GRADE_EMOJI,
    "industrial": INDUSTRIAL_GRADE_EMOJI,
    "milspec": MILSPEC_EMOJI,
    "restricted": RESTRICTED_EMOJI,
    "classified": CLASSIFIED_EMOJI,
    "covert": COVERT_EMOJI,
    "contraband": CONTRABAND_EMOJI,
}

case_rarity_odds = {
    "rare items": 0.9974,
    "covert": 0.9910,
    "classified": 0.9590,
    "restricted": 0.7992,
    "milspec": 0.0000,
}

conditions = [
    "Factory New",
    "Minimal Wear",
    "Field Tested",
    "Well Worn",
    "Battle Scarred",
]

trade_up_rarity_dict = {
    "consumer": "industrial",
    "industrial": "milspec",
    "milspec": "restricted",
    "restricted": "classified",
    "classified": "covert",
}

# index of each condition in above list mapped to the lower bound of their ranges
case_wear_ranges_lower = {4: 0.45, 3: 0.38, 2: 0.15, 1: 0.07, 0: 0.00}
# index of each condition in above list mapped to the upper bound of their ranges
case_wear_ranges_upper = {4: 1.0, 3: 0.45, 2: 0.38, 1: 0.15, 0: 0.07}
