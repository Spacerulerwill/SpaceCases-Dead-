import requests
import html
from src.util.constants import err_code_dict
import json
from src.util.format import remove_skin_name_formatting

# only get prices of items of these types
VALID_TYPES = ["Weapon", "Knife", "Gloves"]

PRICE_TIME_RANGES = ["24_hours", "7_days", "30_days", "all_time"]

def get_api_data():
    api_fetch = requests.get("http://csgobackpack.net/api/GetItemsList/v2/")
    status_code = api_fetch.status_code

    if status_code != 200:
        print(f"Status code {status_code} when fetching api data: {err_code_dict[status_code]}")
        return {}

    return json.loads(html.unescape(api_fetch.text))

def add_skin_prices(input_dict, api_data):    
    items_list = api_data["items_list"]

    #fetch prices from resulting json
    for value in items_list.values():
        if value["type"] in VALID_TYPES:
            formatted_name = value["name"]

            #vanilla knives have no skin name so no pipe
            if "|" not in formatted_name and value["weapon_type"] == "Knife":
                formatted_name += " | Vanilla"


            unformatted_name = remove_skin_name_formatting(formatted_name)
            # try to get the most recent pricing
            for time_range in PRICE_TIME_RANGES:
                try:
                    input_dict[unformatted_name] = value["price"][time_range]["average"]
                    break
                except KeyError:
                    pass
            else: #if none are found, no price data
                input_dict[unformatted_name] = None

    print("Added prices!")

def add_api_static_data(input_dict, api_data):
    items_list = api_data["items_list"]
    for value in items_list.values():
        if value["type"] in VALID_TYPES:
            formatted_name = value["name"]

            if "|" not in formatted_name and value["weapon_type"] == "Knife":
                formatted_name += " | Vanilla"

            unformatted_name = remove_skin_name_formatting(formatted_name)

            if unformatted_name in input_dict:
                input_dict[unformatted_name]["image_url"] = "https://community.akamai.steamstatic.com/economy/image/" + value["icon_url"]
                input_dict[unformatted_name]["rarity_color"] = value["rarity_color"]
                input_dict[unformatted_name]["rarity"] = value["rarity"]
                if "tournament" in value:
                    input_dict[unformatted_name]["tournament"] = value["tournament"]
            else:
                input_dict[unformatted_name] = {
                    "image_url": "https://community.akamai.steamstatic.com/economy/image/" + value["icon_url"],
                    "rarity_color": value["rarity_color"],
                    "rarity": value["rarity"]
                }

                if "tournament" in value:
                    input_dict[unformatted_name]["tournament"] = value["tournament"]
                     
    print("Added weapon static data")