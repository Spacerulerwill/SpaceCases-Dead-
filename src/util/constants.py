from src.util.emojis import *

PREFIX = "cs "
TWELVE_HOURS = 43200
ONE_DAY = 86400
KEY_PRICE = 250

DEFAULT_INVENTORY_SIZE = 5
INVENTORY_ELEMS_PER_PAGE = 10
LEADERBOARD_ELEMS_PER_PAGE = 10
MAX_THREADS = 30

ROOM_DELETION_TIME = 900

#rarity to color 
rarity_color_dict = {
    "Consumer": 11584473,
    "Industrial": 6199513,
    "Milspec": 4942335,
    "Restricted": 8931327,
    "Classified": 13839590,
    "Covert": 15420235,
    "Contraband": 14986809
}

rarity_emoji_dict = {
    "Consumer": CONSUMER_GRADE_EMOJI,
    "Industrial": INDUSTRIAL_GRADE_EMOJI,
    "Milspec": MILSPEC_EMOJI,
    "Restricted": RESTRICTED_EMOJI,
    "Classified": CLASSIFIED_EMOJI,
    "Covert": COVERT_EMOJI,
    "Contraband": CONTRABAND_EMOJI 
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
    "Battle Scarred"
]

err_msg_type_dict = {
    "int": "an integer"
}

#index of each condition in above list mapped to the lower bound of their ranges
case_wear_ranges_lower = {
    4: 0.45,
    3: 0.38,
    2: 0.15,
    1: 0.07,
    0: 0.00
}
#index of each condition in above list mapped to the upper bound of their ranges
case_wear_ranges_upper = {
    4: 1.0,
    3: 0.45,
    2: 0.38,
    1: 0.15,
    0: 0.07
}
