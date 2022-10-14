PREFIX = "cs "

KEY_PRICE = 2.5

err_code_dict = {
    301: "Redirected to to a different endpoint!",
    400: "Bad request!",
    401: "Authentication error!",
    403: "Forbidden access!",
    404: "Not found!",
    503: "Server not ready to handle request!"
}

wear_dict = {
    "fn": "(Factory New)",
    "mw": "(Minimal Wear)",
    "ft": "(Field-Tested)",
    "ww": "(Well-Worn)",
    "bs": "(Battle-Scarred)",
    "no_wear": ""
}

case_rarity_odds = {
    "rare-item": 0.9974,
    "covert": 0.9910,
    "classified": 0.9590,
    "restricted": 0.7992,
    "milspec": 0.0000,
}

case_wear_ranges = {
    "(Battle-Scarred)": 0.45,
    "(Well-Worn)": 0.38,
    "(Field-Tested)": 0.15,
    "(Minimal Wear)": 0.07,
    "(Factory New)": 0.00
}