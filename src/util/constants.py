PREFIX = "cs "

KEY_PRICE = 250

INVENTORY_ELEMS_PER_PAGE = 5

rarity_color_dict = {
    "Milspec": 4942335,
    "Restricted": 8931327,
    "Classified": 13839590,
    "Covert": 15420235,
    "Contraband": 14986809
}

case_rarity_odds = {
    "rares items": 0.9974,
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

#index of each condition in above list mapped to the lower bound of their ranges
case_wear_ranges = {
    4: 0.45,
    3: 0.38,
    2: 0.15,
    1: 0.07,
    0: 0.00
}