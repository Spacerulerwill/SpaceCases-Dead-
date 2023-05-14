"""
Copyright (C) 2022 William Redding - All Rights Reserved

The home of all cross file constants (to avoid circular dependencies)

See end of file for licence details
"""

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

NO_PRICE_FOUND = 5000000

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPRGX/104.0.4480.100"
}

# rarity to color
rarity_color_dict = {
    "consumer": 11584473,
    "industrial": 6199513,
    "milspec": 4942335,
    "high": 4942335,
    "restricted": 8931327,
    "remarkable": 8931327,
    "classified": 13839590,
    "exotic": 13839590,
    "covert": 15420235,
    "extraordinary": 15420235,
    "contraband": 14986809,
}

rarity_emoji_dict = {
    "consumer": CONSUMER_GRADE_EMOJI,
    "industrial": INDUSTRIAL_GRADE_EMOJI,
    "milspec": MILSPEC_EMOJI,
    "high": MILSPEC_EMOJI,
    "restricted": RESTRICTED_EMOJI,
    "remarkable": RESTRICTED_EMOJI,
    "classified": CLASSIFIED_EMOJI,
    "exotic": CLASSIFIED_EMOJI,
    "covert": COVERT_EMOJI,
    "extraordinary": COVERT_EMOJI,
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

# index of each condition in above list mapped to the lower bound of their ranges
case_wear_ranges_lower = {4: 0.45, 3: 0.38, 2: 0.15, 1: 0.07, 0: 0.00}
# index of each condition in above list mapped to the upper bound of their ranges
case_wear_ranges_upper = {4: 1.0, 3: 0.45, 2: 0.38, 1: 0.15, 0: 0.07}

# higher lower game constants
COSTS_MORE = True
COSTS_LESS = False

HL_MIN_GUESS = 5
HL_MAX_GUESS = 10

HL_PRICE = 250
HL_REWARD = lambda difficulty: ((difficulty - HL_MIN_GUESS) * 250) + HL_PRICE + 750

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