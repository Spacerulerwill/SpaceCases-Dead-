"""
Webscraper script used to data for the skins in csgo
"""

from bs4 import BeautifulSoup
from functools import partial
import requests
import concurrent.futures
import re
from src.util.string_util import remove_skin_name_formatting
from src.util.constants import case_wear_ranges_lower, MAX_THREADS, HTTP_HEADERS
from src.util import database
from decimal import Decimal
from timeit import default_timer as timer
from datetime import timedelta

NO_PRICE_FOUND = 300000

endpoints = [
    # pistols
    "weapon/CZ75-Auto",
    "weapon/Desert+Eagle",
    "weapon/Dual+Berettas",
    "weapon/Five-SeveN",
    "weapon/Glock-18",
    "weapon/P2000",
    "weapon/P250",
    "weapon/R8+Revolver",
    "weapon/Tec-9",
    "weapon/USP-S",
    # rifles
    "weapon/AK-47",
    "weapon/AUG",
    "weapon/AWP",
    "weapon/FAMAS",
    "weapon/G3SG1",
    "weapon/Galil AR",
    "weapon/M4A1-S",
    "weapon/M4A4",
    "weapon/SCAR-20",
    "weapon/SG+553",
    "weapon/SSG+08",
    # smgs
    "weapon/MAC-10",
    "weapon/MP5-SD",
    "weapon/MP7",
    "weapon/MP9",
    "weapon/PP-Bizon",
    "weapon/P90",
    "weapon/UMP-45",
    # heavy
    "weapon/MAG-7",
    "weapon/Nova",
    "weapon/Sawed-Off",
    "weapon/XM1014",
    "weapon/M249",
    "weapon/Negev",
    # knives
    "weapon/Nomad+Knife",
    "weapon/Skeleton+Knife",
    "weapon/Survival+Knife",
    "weapon/Paracord+Knife",
    "weapon/Classic+Knife",
    "weapon/Bayonet",
    "weapon/Bowie+Knife",
    "weapon/Butterfly+Knife",
    "weapon/Falchion+Knife",
    "weapon/Flip+Knife",
    "weapon/Gut+Knife",
    "weapon/Huntsman+Knife",
    "weapon/Karambit",
    "weapon/M9+Bayonet",
    "weapon/Navaja+Knife",
    "weapon/Shadow+Daggers",
    "weapon/Stiletto+Knife",
    "weapon/Talon+Knife",
    "weapon/Ursus+Knife",
    # gloves
    "gloves?page=1",
    "gloves?page=2",
]

inspect_button_condition_dict = {
    "Inspect (FN)": "factory new ",
    "Inspect (MW)": "minimal wear ",
    "Inspect (FT)": "field tested ",
    "Inspect (WW)": "well worn ",
    "Inspect (BS)": "battle scarred ",
}

condition_index_dict = {
    "factory new": 0,
    "minimal wear": 1,
    "field tested": 2,
    "well worn": 3,
    "battle scarred": 4,
    "stattrak factory new": 0,
    "stattrak minimal wear": 1,
    "stattrak field tested": 2,
    "stattrak well worn": 3,
    "stattrak battle scarred": 4,
    "souvenir factory new": 0,
    "souvenir minimal wear": 1,
    "souvenir field tested": 2,
    "souvenir well worn": 3,
    "souvenir battle scarred": 4,
}


# scraping a weapon endpoint (all the skins for a weapon) - adds them to a skin_links list
def scrape_endpoint(skin_links, endpoint):
    r = requests.get(f"https://csgostash.com/{endpoint}", headers=HTTP_HEADERS)
    soup = BeautifulSoup(r.content, "html.parser")

    # extract href from a tag of ever div with class details link
    details_links = [
        link_div.find("a")["href"]
        for link_div in soup.find_all("div", {"class": "details-link"})
    ]
    skin_links += details_links


def scrape_skin_link(result, container_data, skin_link):
    # get html source
    r = requests.get(skin_link, headers=HTTP_HEADERS)
    soup = BeautifulSoup(r.content, "html.parser")

    # get skins formatted and unformatted name
    formatted_name = soup.select_one("div.well.result-box.nomargin").find("h2").text

    is_vanilla_knife = "★ (Vanilla)" in formatted_name  # vanilla knives are difficult

    unformatted_name = remove_skin_name_formatting(formatted_name)

    # check if available in stattrak, souvenir or none and choose the right condition prefixes
    has_stattrak_variant = soup.find("div", {"class": "stattrak"}) != None
    has_souvenir_variant = soup.find("div", {"class": "souvenir"}) != None

    # min and max floats
    markers = soup.find_all("div", {"class": "marker-value"})

    if markers != []:
        min_float = float(markers[0].text)
        max_float = float(markers[1].text)
    else:
        min_float = 0.0
        max_float = 1.0

    # best and worst conditions
    for index, lower_value in case_wear_ranges_lower.items():
        if min_float >= lower_value:
            best_condition_index = index
            break

    # best and worst conditions
    for index, lower_value in case_wear_ranges_lower.items():
        if max_float >= lower_value:
            worst_condition_index = index
            break

    # rarity
    rarity_div = soup.find("div", {"class": ["quality"]})
    rarity = rarity_div["class"][1].replace("color-", "").lower()

    # can it be used in a trade up? Find its container name, check it is not the last tier in its respective container
    collection = remove_skin_name_formatting(
        soup.find(
            "div", {"class": "skin-details-collection-container-wrapper"}
        ).text.strip()
    )

    weapon_type = rarity_div.text.split(" ")[-1].strip()

    # Knives, Gloves, Souvenirs can NEVER be traded up
    if (
        weapon_type in ["Knife", "Gloves"]
        or "Souvenir" in formatted_name
        or rarity == "covert"
    ):
        can_tradeup = False
    else:  # is the rarity the last key? if it is, no trade up!
        can_tradeup = (
            list(container_data[collection]["items"].keys()).index(rarity)
            != len(container_data[collection]["items"]) - 1
        )

    # add prices
    table = soup.find(
        "table",
        {
            "class": [
                "table table-hover",
                "table-bordered",
                "table-condensed",
                "price-details-table dataTable",
                "no-footer",
            ]
        },
    )
    table_body = table.find("tbody")
    table_rows = table_body.find_all("tr")

    for row in table_rows:
        data_cells = row.find_all("td")
        row_formatted_condition = data_cells[0].text.replace("\n", "").strip()

        row_unformatted_condition = remove_skin_name_formatting(row_formatted_condition)

        steam_price = data_cells[1].text.replace("\n", "").strip()
        bitskins_price = data_cells[5].text.replace("\n", "").strip()

        price = NO_PRICE_FOUND

        if steam_price != "":
            price_str = re.sub(r"[^\d.]", "", steam_price)
            price = int(Decimal(price_str) * 100)
        elif bitskins_price != "":
            price_str = re.sub(r"[^\d.]", "", bitskins_price)
            price = int(Decimal(price_str) * 100)

        # if a vanilla knife, create 5 identical entries with different wear ratings in their names (circumvents difficulty later for vanilla knives)
        if is_vanilla_knife:
            for condition in [
                "Factory New",
                "Minimal Wear",
                "Field Tested",
                "Well Worn",
                "Battle Scarred",
                "StatTrak Factory New",
                "StatTrak Minimal Wear",
                "StatTrak Field Tested",
                "StatTrak Well Worn",
                "StatTrak Battle Scarred",
            ]:
                result["skins"][condition.lower() + " " + unformatted_name] = {
                    "formatted_name": condition + " " + formatted_name,
                    "item_type": "weapon",
                    "no_wear_formatted_name": formatted_name,
                    "price": price,
                    "rarity": rarity,
                    "type": weapon_type,
                    "min_float": min_float,
                    "max_float": max_float,
                    "condition_index": condition_index_dict[condition.lower()],
                    "best_condition_index": best_condition_index,
                    "worst_condition_index": worst_condition_index,
                    "has_stattrak_variant": has_stattrak_variant,
                    "has_souvenir_variant": has_souvenir_variant,
                    "can_tradeup": can_tradeup,
                }

            # non wear version
            result["no_wear_skins"][unformatted_name] = {
                "formatted_name": formatted_name,
                "item_type": "weapon",
                "rarity": rarity,
                "type": weapon_type,
                "min_float": min_float,
                "max_float": max_float,
                "best_condition_index": best_condition_index,
                "worst_condition_index": worst_condition_index,
                "has_stattrak_variant": has_stattrak_variant,
                "has_souvenir_variant": has_souvenir_variant,
                "can_tradeup": can_tradeup,
            }

        else:  # otherwise do as usual
            condition_index = condition_index_dict[row_unformatted_condition]

            result["skins"][row_unformatted_condition + " " + unformatted_name] = {
                "formatted_name": row_formatted_condition + " " + formatted_name,
                "item_type": "weapon",
                "no_wear_formatted_name": formatted_name,
                "price": price,
                "rarity": rarity,
                "type": weapon_type,
                "min_float": min_float,
                "max_float": max_float,
                "condition_index": condition_index,
                "best_condition_index": best_condition_index,
                "worst_condition_index": worst_condition_index,
                "has_stattrak_variant": has_stattrak_variant,
                "has_souvenir_variant": has_souvenir_variant,
                "can_tradeup": can_tradeup,
            }

            # add the non wear versions
            result["no_wear_skins"][unformatted_name] = {
                "formatted_name": formatted_name,
                "item_type": "weapon",
                "rarity": rarity,
                "type": weapon_type,
                "min_float": min_float,
                "max_float": max_float,
                "condition_index": condition_index,
                "best_condition_index": best_condition_index,
                "worst_condition_index": worst_condition_index,
                "has_stattrak_variant": has_stattrak_variant,
                "has_souvenir_variant": has_souvenir_variant,
                "can_tradeup": can_tradeup,
            }

            # if not knife or gloves, add its container (or collection)
            if weapon_type not in ["Knife", "Gloves"]:
                result["skins"][row_unformatted_condition + " " + unformatted_name][
                    "container"
                ] = collection
                result["no_wear_skins"][unformatted_name]["container"] = collection

    # add images and inspect links
    # if its a vanilla knife, add the same image to each wear
    if is_vanilla_knife:
        img_url = soup.find("img", {"class": "main-skin-img"})["src"]
        inspect_url = soup.find("a", {"class": "inspect-button-skin"})["href"]

        for condition in [
            "Factory New",
            "Minimal Wear",
            "Field Tested",
            "Well Worn",
            "Battle Scarred",
            "StatTrak Factory New",
            "StatTrak Minimal Wear",
            "StatTrak Field Tested",
            "StatTrak Well Worn",
            "StatTrak Battle Scarred",
        ]:
            result["skins"][condition.lower() + " " + unformatted_name][
                "image_url"
            ] = img_url
            result["skins"][condition.lower() + " " + unformatted_name][
                "inspect_url"
            ] = inspect_url

    else:  # otherwise add different images to each wear
        image_buttons_div = soup.find(
            "div", {"class": ["btn-group-sm", "btn-group-justified"]}
        )
        image_buttons = image_buttons_div.find_all("a")

        for button in image_buttons:
            text = button.text.strip()
            wear = inspect_button_condition_dict[text]
            url = button["data-hoverimg"]
            inspect_url = button["href"]

            result["skins"][wear + unformatted_name]["image_url"] = url
            result["skins"][wear + unformatted_name]["inspect_url"] = inspect_url

            if has_stattrak_variant:
                result["skins"]["stattrak " + wear + unformatted_name][
                    "image_url"
                ] = url
                result["skins"]["stattrak " + wear + unformatted_name][
                    "inspect_url"
                ] = inspect_url
            if has_souvenir_variant:
                result["skins"]["souvenir " + wear + unformatted_name][
                    "image_url"
                ] = url
                result["skins"]["souvenir " + wear + unformatted_name][
                    "inspect_url"
                ] = inspect_url


sticker_links = [
    f"https://csgostash.com/stickers/regular?page={i+1}" for i in range(14)
] + [f"https://csgostash.com/stickers/tournament?page={i+1}" for i in range(95)]
sticker_modifiers = ["foil", "gold", "holo", "glitter", "lenticular"]


def scrape_sticker_link(result, sticker_link):
    # get html source
    r = requests.get(sticker_link, headers=HTTP_HEADERS)
    soup = BeautifulSoup(r.content, "html.parser")

    result_boxes = soup.select("div.well.result-box.nomargin")
    for result_box in result_boxes:
        h3 = result_box.find("h3")

        if h3 is None:
            continue

        formatted_sticker_name = h3.text.strip()
        formatted_tournament_name = result_box.find("h4")

        any((modifier := mod) in formatted_sticker_name for mod in sticker_modifiers)

        if formatted_tournament_name is not None:
            formatted_tournament_name = formatted_tournament_name.find("a").text.strip()
            formatted_sticker_name = (
                f"{formatted_sticker_name} | {formatted_tournament_name}"
            )

        unformatted_sticker_name = remove_skin_name_formatting(formatted_sticker_name)

        price_div = result_box.find("div", {"class": "price"})
        price_str = price_div.find("a").text.strip()

        if price_str == "No Recent Price":
            price = NO_PRICE_FOUND
        else:
            price_str = re.sub(r"[^\d.]", "", price_str)
            price = int(Decimal(price_str) * 100)

        image_url = result_box.find("img")["src"]

        rarity = (
            result_box.find("div", {"class": "quality"})
            .text.split(" ")[0]
            .lower()
            .strip()
        )

        result["skins"][unformatted_sticker_name] = {
            "item_type": "sticker",
            "formatted_name": formatted_sticker_name,
            "modifier": modifier,
            "price": price,
            "rarity": rarity,
            "image_url": image_url,
            "can_tradeup": False,
        }


def csgostash_scrape(scrape_containers: bool = False) -> dict:
    skin_links = []
    result = {"_id": "skin-data", "skins": {}, "no_wear_skins": {}}

    if scrape_containers:
        database.scrape_container_data()

    all_container_data = {
        **database.collections,
        **database.containers,
    }  # we need the collections and cases data, not the souvenir packages and cases data.

    print("Scraping skin data...")
    start = timer()

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(partial(scrape_endpoint, skin_links), endpoints)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(partial(scrape_skin_link, result, all_container_data), skin_links)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(partial(scrape_sticker_link, result), sticker_links)

    end = timer()
    print(f"Executed in {timedelta(seconds=end-start)}")
    return result
