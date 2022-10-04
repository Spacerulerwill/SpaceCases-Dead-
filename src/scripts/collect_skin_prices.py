
import requests
from src.util.constants import err_code_dict

# only get prices of items of these types
VALID_TYPES = ["Weapon", "Knife", "Gloves"]

PRICE_TIME_RANGES = ["24_hours", "7_days", "30_days", "all_time"]

def get_api_data():
    api_fetch = requests.get("http://csgobackpack.net/api/GetItemsList/v2/")
    status_code = api_fetch.status_code

    if status_code != 200:
        print(f"Status code {status_code} when fetching api data: {err_code_dict[status_code]}")
        return {}

    return api_fetch.json()

def add_skin_prices(input_dict, api_data):    
    items_list = api_data["items_list"]

    #fetch prices from resulting json
    for value in items_list.values():
        if value["type"] in VALID_TYPES:
            # try to get the most recent pricing
            for time_range in PRICE_TIME_RANGES:
                try:
                    input_dict[value["name"]] = value["price"][time_range]["average"]
                    break
                except KeyError:
                    pass
            else: #if none are found, no price data
                input_dict[value["name"]] = None

    print("Added prices!")

def add_skin_images(input_dict, api_data):
    items_list = api_data["items_list"]
    for value in items_list.values():
        if value["type"] in VALID_TYPES:
            name= value["name"]

            if name in input_dict:
                input_dict[name]["image_url"] = "community.akamai.steamstatic.com/economy/image/" + value["icon_url"]
            else:
                input_dict[name] = {"image_url": "community.akamai.steamstatic.com/economy/image/" + value["icon_url"]}
    print("Added weapon images")