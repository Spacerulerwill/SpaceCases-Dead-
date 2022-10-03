# this is a script to generate price data for all the price data for items in counter-strike
# it is run at a fixed time interval while the bot is running

import requests
from src.util.constants import err_code_dict

# only get prices of items of these types
VALID_TYPES = ["Weapon", "Knife", "Gloves"]

PRICE_TIME_RANGES = ["24_hours", "7_days", "30_days", "all_time"]

def get_skin_prices():
    prices = {}

    api_fetch = requests.get("http://csgobackpack.net/api/GetItemsList/v2/")
    status_code = api_fetch.status_code

    if status_code != 200:
        print(f"Status code {status_code} when fetching skin prices: {err_code_dict[status_code]}")
        return {}
    
    items_list = api_fetch.json()["items_list"]

    #fetch prices from resulting json
    for value in items_list.values():
        if value["type"] in VALID_TYPES:
            # try to get the most recent pricing
            for time_range in PRICE_TIME_RANGES:
                try:
                    prices[value["name"]] = value["price"][time_range]["average"]
                    break
                except KeyError:
                    pass
            else: #if none are found, no price data
                prices[value["name"]] = None

    print("Successfully Scraped Prices!")
    return prices