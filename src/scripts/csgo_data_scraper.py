"""
Copyright (C) 2023 William Redding

Webscraper script that scrapes csgoskins.gg for game data needed, including:
* Skin data
* Containers data
* Sticker Data

See end of file for licence details
"""

import re
import logging
from copy import deepcopy
import requests
from decimal import Decimal
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from src.util.constants import (
    MAX_THREADS,
    HTTP_HEADERS,
    case_wear_ranges_lower,
    conditions,
    NO_PRICE_FOUND,
)
from src.util.string_util import remove_skin_name_formatting


def get_links_from_page(item_links: list[str], url: str):
    request = requests.get(url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "html.parser")

    # find all image divs
    boxes = soup.select("div.bg-gray-800.rounded.shadow-md.relative.flex.flex-wrap")

    # extract hrefs and append to skin_links
    item_links += [box.find("a")["href"] for box in boxes]


# region === ITEM SCRAPING ===
gun_endpoints = (
    [
        f"https://csgoskins.gg/?type=1&order=lowest_price&page={i+1}" for i in range(8)
    ]  # pistols
    + [
        f"https://csgoskins.gg/?type=2&order=lowest_price&page={i+1}" for i in range(5)
    ]  # smg
    + [
        f"https://csgoskins.gg/?type=3&order=lowest_price&page={i+1}" for i in range(6)
    ]  # rifles
    + [
        f"https://csgoskins.gg/?type=4&order=lowest_price&page={i+1}" for i in range(3)
    ]  # shotguns
    + [
        f"https://csgoskins.gg/?type=5&order=lowest_price&page={i+1}" for i in range(3)
    ]  # sniper rifle
    + [
        f"https://csgoskins.gg/?type=6&order=lowest_price&page={i+1}" for i in range(1)
    ]  # machine gun
)

rare_item_endpoints = [
    f"https://csgoskins.gg/?type=8&order=lowest_price&page={i+1}" for i in range(9)
] + [  # knife
    f"https://csgoskins.gg/?type=11&order=lowest_price&page={i+1}" for i in range(2)
]  # gloves

sticker_endpoints = [
    f"https://csgoskins.gg/categories/sticker?page={i+1}" for i in range(140)
]


def scrape_weapon_skin_link(item_data: dict, url: str):
    request = requests.get(url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "html.parser")

    # get name
    formatted_name = soup.select_one("h1.text-2xl.sm\:text-3xl.font-bold").text

    logging.debug(f"Scraping item: {formatted_name}")
    unformatted_name = remove_skin_name_formatting(formatted_name)

    is_vanilla_knife = " | Vanilla" in formatted_name  # vanilla knives are difficult

    # float range
    if is_vanilla_knife:
        min_float = 0.0
        max_float = 1.0
    else:
        float_spans = soup.select("span.text-sm.absolute")
        min_float = float(float_spans[0].text)
        max_float = float(float_spans[1].text)

    # weapon type
    summary_div = soup.find("div", {"class": None})
    summary_boxes = summary_div.select("div.flex.px-4.py-2")
    type_summary_box = summary_boxes[1].select_one("div.flex-grow.text-right")
    type = type_summary_box.text.strip().lower()

    # remove star
    if type in ["knife", "gloves"]:
        formatted_name = formatted_name.replace("★", "").strip()

    # rarity
    item_class_divs = soup.select("div.text-center.mb-1")
    rarity = item_class_divs[0].text.replace("-", "").split()[0].strip().lower()

    # whether it has a stattrak or souvenir variant
    if len(item_class_divs) > 1:
        has_stattrak_variant = item_class_divs[1].text.strip() == "StatTrak"

        if not has_stattrak_variant:
            has_souvenir_variant = item_class_divs[1].text.strip() == "Souvenir"
        else:
            has_souvenir_variant = False
    else:
        has_stattrak_variant = False
        has_souvenir_variant = False

    # condition indexes
    # best and worst conditions
    for index, lower_value in case_wear_ranges_lower.items():
        if min_float >= lower_value:
            best_condition_index = index
            break

    # best and worst conditions
    for index, lower_value in case_wear_ranges_lower.items():
        if max_float > lower_value:
            worst_condition_index = index

    # prices and image urls
    price_divs = soup.find_all("a", {"class": "version-link"})

    # create data for skin without wear
    data = {
        "item_type": "weapon",
        "formatted_name": formatted_name,
        "rarity": rarity,
        "type": type,
        "min_float": min_float,
        "max_float": max_float,
        "worst_condition_index": worst_condition_index,
        "best_condition_index": best_condition_index,
        "has_stattrak_variant": has_stattrak_variant,
        "has_souvenir_variant": has_souvenir_variant,
        "can_tradeup": False,
        "tradeup_result_pool": [],
    }
    item_data["no_wear_skins"][unformatted_name] = data

    # if vanilla knife, create identical copies for each wear
    if is_vanilla_knife:
        image_url = price_divs[0]["data-image-url"]

        # non stattrak version
        price_div_text = price_divs[0].text.strip()

        if "No offers" in price_div_text:
            price = NO_PRICE_FOUND
        else:
            price_str = price_div_text.split("$")[1].strip()
            price_str = re.sub(r"[^\d.]", "", price_str)
            price = int(Decimal(price_str) * 100)

        for condition_index, formatted_condition in enumerate(
            [
                "Factory New",
                "Minimal Wear",
                "Field-Tested",
                "Well-Worn",
                "Battle-Scarred",
            ]
        ):
            unformatted_condition = remove_skin_name_formatting(formatted_condition)

            new_data = deepcopy(data)

            new_data["price"] = price
            new_data["no_wear_formatted_name"] = formatted_name
            new_data["image_url"] = image_url
            new_data["condition_index"] = condition_index
            new_data["formatted_name"] = formatted_condition + " " + formatted_name

            item_data["items"][
                unformatted_condition + " " + unformatted_name
            ] = new_data

        # stattrak version
        price_div_text = price_divs[1].text.strip()

        if "No offers" in price_div_text:
            price = NO_PRICE_FOUND
        else:
            price_str = price_div_text.split("$")[1].strip()
            price_str = re.sub(r"[^\d.]", "", price_str)
            price = int(Decimal(price_str) * 100)

        for condition_index, formatted_condition in enumerate(
            [
                "StatTrak Factory New",
                "StatTrak Minimal Wear",
                "StatTrak Field-Tested",
                "StatTrak Well-Worn",
                "StatTrak Battle-Scarred",
            ]
        ):
            unformatted_condition = remove_skin_name_formatting(formatted_condition)

            new_data = deepcopy(data)

            new_data["price"] = price
            new_data["no_wear_formatted_name"] = formatted_name
            new_data["image_url"] = image_url
            new_data["formatted_name"] = formatted_condition + " " + formatted_name
            new_data["condition_index"] = condition_index

            item_data["items"][
                unformatted_condition + " " + unformatted_name
            ] = new_data
    else:
        # iterate through price divs, getting data
        for count, price_div in enumerate(price_divs):
            price_div_text = price_div.text.strip()

            if "Not Possible" in price_div_text:
                continue

            image_url = price_div["data-image-url"]

            if "No offers" in price_div_text:
                price = NO_PRICE_FOUND
                formatted_condition = (
                    price_div_text.replace("No offers", "")
                    .strip()
                    .replace("\n\n\n", " ")
                )
                unformatted_condition = remove_skin_name_formatting(formatted_condition)
            else:
                price_div_text = price_div_text.split("$")
                formatted_condition = price_div_text[0].strip().replace("\n\n\n", " ")
                unformatted_condition = remove_skin_name_formatting(formatted_condition)
                price_str = price_div_text[1].strip()
                price_str = re.sub(r"[^\d.]", "", price_str)
                price = int(Decimal(price_str) * 100)

            # add wear specific information
            new_data = deepcopy(data)
            new_data["price"] = price
            new_data["formatted_name"] = formatted_condition + " " + formatted_name
            new_data["condition_index"] = count % 5
            new_data["no_wear_formatted_name"] = formatted_name
            new_data["image_url"] = image_url

            item_data["items"][
                unformatted_condition + " " + unformatted_name
            ] = new_data


def scrape_sticker_page(item_data: dict, url: str):
    try:
        request = requests.get(url, headers=HTTP_HEADERS)
        soup = BeautifulSoup(request.content, "html.parser")

        sticker_boxes = soup.select(
            "div.bg-gray-800.rounded.shadow-md.relative.flex.flex-wrap"
        )

        for box in sticker_boxes:
            h2 = box.find("h2")
            spans = h2.find_all("span")

            tournament_name = spans[0].text.strip()
            formatted_sticker_name = spans[1].text.strip()

            if tournament_name != "Sticker":
                formatted_sticker_name += f" | {tournament_name}"

            unformatted_sticker_name = remove_skin_name_formatting(
                formatted_sticker_name
            )

            image_url = box.find("img")["src"]
            price_str = box.select_one(
                "div.left-4.right-4.text-center.text-lg.absolute"
            ).text.strip()

            if price_str == "No Price Data":
                price = NO_PRICE_FOUND
            else:
                price_str = re.sub(r"[^\d.]", "", price_str)
                price = int(Decimal(price_str) * 100)

            rarity = (
                box.select_one(
                    "div.left-4.right-4.text-center.text-sm.rounded-xl.text-black.absolute.truncate"
                )
                .text.split()[0]
                .lower()
            )

            item_data["items"][unformatted_sticker_name] = {
                "item_type": "sticker",
                "formatted_name": formatted_sticker_name,
                "price": price,
                "rarity": rarity,
                "image_url": image_url,
                "can_tradeup": False,
            }
    except Exception as e:
        print(e)


# endregion


# region === CONTAINER SCRAPING ===
def calculate_container_odds(items_dict: dict) -> dict:
    # the most common is 80%, each rarity above is 5 times less likely
    rarity_odds = {
        rarity: 0.8 * 0.2**count for count, rarity in enumerate(items_dict.keys())
    }

    # sum of series: 0.8 * 0.2**X does not equal 1, therefore we must make them total one to avoid any boundry cases
    sum_odds = sum(rarity_odds.values())
    add_to_each = (1 - sum_odds) / len(items_dict)

    rarity_odds = {rarity: odd + add_to_each for rarity, odd in rarity_odds.items()}

    final_rarity_odds = {}

    odds = list(rarity_odds.values())
    for count, rarity in enumerate(rarity_odds.keys()):
        final_rarity_odds[rarity] = sum(odds[0:count])

    # reverse dict
    return dict(reversed(final_rarity_odds.items()))


weapon_case_endpoint = "https://csgoskins.gg/categories/weapon-case?page=1"

souvenir_package_endpoints = [
    f"https://csgoskins.gg/categories/souvenir-package?page={i+1}" for i in range(3)
]

package_endpoints = []

sticker_capsule_endpoints = [
    f"https://csgoskins.gg/categories/sticker-capsule?page={i+1}" for i in range(2)
] + [f"https://csgoskins.gg/categories/autograph-capsule?page={i+1}" for i in range(3)]


def scrape_case_link(weapon_case_data: dict, item_data: dict, url: str):
    # open container page, get price name and link to items
    request = requests.get(url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "lxml")

    name_h1 = soup.select_one("body > main > div > div.w-full.px-4.pb-4 > h1")
    formatted_case_name = name_h1.text.strip()
    unformatted_case_name = remove_skin_name_formatting(formatted_case_name)

    # get price
    side_bar = soup.select_one(
        "body > main > div > div.w-full.sm\\:w-full.md\\:w-full.lg\\:w-2\\/5.xl\\:w-1\\/3.\\32 xl\\:w-1\\/3.p-4.flex-none"
    )

    statistics_box = side_bar.find_all("div", {"class": None})[1]
    price_stat = statistics_box.select_one(
        "div.shadow-md.bg-gray-800.rounded.mt-4 > div:nth-child(1)"
    )
    price_str = price_stat.find_all("div")[1].text.strip()
    price_str = re.sub(r"[^\d.]", "", price_str)
    price = int(Decimal(price_str) * 100)

    # image url
    image_url = soup.select_one("#main-image")["src"]

    data = {
        "type": "case",
        "price": price,
        "formatted_name": formatted_case_name,
        "image_url": image_url,
        "odds": None,
        "items": {
            "consumer": [],
            "industrial": [],
            "milspec": [],
            "restricted": [],
            "classified": [],
            "covert": [],
            "rare items": [],
        },
        "all items": [],
    }

    items_page_url = soup.select_one(
        "body > main > div > div.w-full.sm\\:w-full.md\\:w-full.lg\\:w-2\\/5.xl\\:w-1\\/3.\\32 xl\\:w-1\\/3.p-4.flex-none > a"
    )["href"]
    rare_items_url = items_page_url + "/specials"

    # open items page get items data
    request = requests.get(items_page_url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "html.parser")

    boxes = soup.select("div.bg-gray-800.rounded.shadow-md.relative.flex.flex-wrap")

    # iterate through cases skins
    for box in boxes[1:]:
        spans = box.find_all("span")

        # get information
        weapon_name = spans[0].text.strip()
        skin_name = spans[1].text.strip()
        unformatted_name = remove_skin_name_formatting(weapon_name + " " + skin_name)

        rarity_div = box.find_all("div")[1]
        rarity = remove_skin_name_formatting(
            rarity_div.text.strip().split()[0].replace("-", "")
        )
        data["items"][rarity].append(unformatted_name)
        data["all items"].append(unformatted_name)

        # set items can_tradeup bool now that we know its container information
        _item_data = item_data["no_wear_skins"][unformatted_name]
        can_tradeup = _item_data["rarity"] != "covert"
        item_data["no_wear_skins"][unformatted_name]["can_tradeup"] = can_tradeup

        for i in range(
            _item_data["best_condition_index"], _item_data["worst_condition_index"] + 1
        ):
            condition = conditions[i].lower()
            item_data["items"][condition + " " + unformatted_name][
                "can_tradeup"
            ] = can_tradeup

        # if has stattrak variant do for that
        if _item_data["has_stattrak_variant"]:
            for i in range(
                _item_data["best_condition_index"],
                _item_data["worst_condition_index"] + 1,
            ):
                condition = conditions[i].lower()
                item_data["items"]["stattrak " + condition + " " + unformatted_name][
                    "can_tradeup"
                ] = can_tradeup

    # open rare items page, get rare itemsdata
    request = requests.get(rare_items_url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "html.parser")

    boxes = soup.select("div.bg-gray-800.rounded.shadow-md.relative.flex.flex-wrap")

    for box in boxes[1:]:
        spans = box.find_all("span")

        weapon_name = spans[0].text.strip()
        skin_name = spans[1].text.strip()
        unformatted_name = remove_skin_name_formatting(weapon_name + " " + skin_name)

        data["items"]["rare items"].append(unformatted_name)
        data["all items"].append(unformatted_name)

    # remove empty rarities
    data["items"] = {rarity: items for rarity, items in data["items"].items() if items}

    # add final information
    data["odds"] = calculate_container_odds(data["items"])
    weapon_case_data[unformatted_case_name] = data


def scrape_package_link(
    souvenir_package_data: dict, item_data: dict, type: str, url: str
):
    # open souvenir package page, get price name and link to items
    request = requests.get(url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "lxml")

    name_h1 = soup.select_one("body > main > div > div.w-full.px-4.pb-4 > h1")
    formatted_case_name = name_h1.text.strip()
    unformatted_case_name = remove_skin_name_formatting(formatted_case_name)

    # get price
    side_bar = soup.select_one(
        "body > main > div > div.w-full.sm\\:w-full.md\\:w-full.lg\\:w-2\\/5.xl\\:w-1\\/3.\\32 xl\\:w-1\\/3.p-4.flex-none"
    )

    statistics_box = side_bar.find_all("div", {"class": None})[1]
    price_stat = statistics_box.select_one(
        "div.shadow-md.bg-gray-800.rounded.mt-4 > div:nth-child(1)"
    )
    price_str = price_stat.find_all("div")[1].text.strip()
    price_str = re.sub(r"[^\d.]", "", price_str)
    price = int(Decimal(price_str) * 100)

    # image url
    image_url = soup.select_one("#main-image")["src"]

    data = {
        "type": type,
        "price": price,
        "formatted_name": formatted_case_name,
        "image_url": image_url,
        "odds": None,
        "items": {
            "consumer": [],
            "industrial": [],
            "milspec": [],
            "restricted": [],
            "classified": [],
            "covert": [],
        },
        "all items": [],
    }

    items_page_url = soup.select_one(
        "body > main > div > div.w-full.sm\\:w-full.md\\:w-full.lg\\:w-2\\/5.xl\\:w-1\\/3.\\32 xl\\:w-1\\/3.p-4.flex-none > a"
    )["href"]
    # open items page get items data
    request = requests.get(items_page_url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "html.parser")

    boxes = soup.select("div.bg-gray-800.rounded.shadow-md.relative.flex.flex-wrap")

    # iterate through cases skins
    for box in boxes:
        spans = box.find_all("span")

        weapon_name = spans[0].text.strip()
        skin_name = spans[1].text.strip()
        unformatted_name = remove_skin_name_formatting(weapon_name + " " + skin_name)

        rarity_div = box.find_all("div")[1]
        rarity = remove_skin_name_formatting(
            rarity_div.text.strip().split()[0].replace("-", "")
        )
        data["items"][rarity].append(unformatted_name)
        data["all items"].append(unformatted_name)

    # remove empty rarities
    data["items"] = {rarity: items for rarity, items in data["items"].items() if items}

    # set can trade_up values
    for _unformatted_name in data["all items"]:
        _item_data = item_data["no_wear_skins"][_unformatted_name]
        can_tradeup = (
            list(data["items"].keys()).index(_item_data["rarity"])
            != len(data["items"]) - 1
        )

        # if has souvenir variant do for that
        if _item_data["has_souvenir_variant"]:
            for i in range(
                _item_data["best_condition_index"],
                _item_data["worst_condition_index"] + 1,
            ):
                condition = conditions[i].lower()
                item_data["items"]["souvenir " + condition + " " + unformatted_name][
                    "can_tradeup"
                ] = False

        # if has stattrak variant do for that
        elif _item_data["has_stattrak_variant"]:
            for i in range(
                _item_data["best_condition_index"],
                _item_data["worst_condition_index"] + 1,
            ):
                condition = conditions[i].lower()
                item_data["items"]["stattrak " + condition + " " + unformatted_name][
                    "can_tradeup"
                ] = can_tradeup

        item_data["no_wear_skins"][unformatted_name]["can_tradeup"] = can_tradeup

        for i in range(
            _item_data["best_condition_index"], _item_data["worst_condition_index"] + 1
        ):
            condition = conditions[i].lower()
            item_data["items"][condition + " " + unformatted_name][
                "can_tradeup"
            ] = can_tradeup

    # add final information
    data["odds"] = calculate_container_odds(data["items"])
    souvenir_package_data[unformatted_case_name] = data


def scrape_sticker_capsule_link(sticker_capsule_data: dict, url: str):
    # open sticker capsule page
    request = requests.get(url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "lxml")

    name_h1 = soup.select_one("body > main > div > div.w-full.px-4.pb-4 > h1")
    formatted_capsule_name = name_h1.text.strip()
    unformatted_capsule_name = remove_skin_name_formatting(formatted_capsule_name)

    # get price
    side_bar = soup.select_one(
        "body > main > div > div.w-full.sm\\:w-full.md\\:w-full.lg\\:w-2\\/5.xl\\:w-1\\/3.\\32 xl\\:w-1\\/3.p-4.flex-none"
    )

    statistics_box = side_bar.find_all("div", {"class": None})[1]
    price_stat = statistics_box.select_one(
        "div.shadow-md.bg-gray-800.rounded.mt-4 > div:nth-child(1)"
    )
    price_str = price_stat.find_all("div")[1].text.strip()
    price_str = re.sub(r"[^\d.]", "", price_str)
    price = int(Decimal(price_str) * 100)

    # image url
    image_url = soup.select_one("#main-image")["src"]

    data = {
        "type": "sticker_capsule",
        "price": price,
        "formatted_name": formatted_capsule_name,
        "image_url": image_url,
        "odds": None,
        "items": {
            "high": [],
            "remarkable": [],
            "exotic": [],
            "extraordinary": [],
            "contraband": [],
        },
        "all items": [],
    }

    items_page_url = soup.select_one(
        "body > main > div > div.w-full.sm\\:w-full.md\\:w-full.lg\\:w-2\\/5.xl\\:w-1\\/3.\\32 xl\\:w-1\\/3.p-4.flex-none > a"
    )["href"]
    # open items page get items data
    request = requests.get(items_page_url, headers=HTTP_HEADERS)
    soup = BeautifulSoup(request.content, "html.parser")

    boxes = soup.select("div.bg-gray-800.rounded.shadow-md.relative.flex.flex-wrap")

    # iterate through cases skins
    for box in boxes:
        spans = box.find_all("span")

        weapon_name = spans[0].text.strip()
        skin_name = spans[1].text.strip()
        unformatted_name = remove_skin_name_formatting(weapon_name + " " + skin_name)

        rarity_div = box.find_all("div")[1]
        rarity = remove_skin_name_formatting(
            rarity_div.text.strip().split()[0].replace("-", "")
        )
        data["items"][rarity].append(unformatted_name)
        data["all items"].append(unformatted_name)

    # remove empty rarities
    data["items"] = {rarity: items for rarity, items in data["items"].items() if items}

    # add final information
    data["odds"] = calculate_container_odds(data["items"])
    sticker_capsule_data[unformatted_capsule_name] = data


def set_tradeup_result_pools(item_data: dict, container_data: dict):
    for name, data in container_data.items():
        if name != "_id" and data["type"] != "sticker_capsule":
            container_rarites = list(data["items"].keys())

            for unformmatted_name in data["all items"]:
                skin_data = item_data["no_wear_skins"][unformmatted_name]

                if skin_data["can_tradeup"]:
                    rarity = skin_data["rarity"]
                    next_rarity = container_rarites[container_rarites.index(rarity) + 1]

                    # set result pool for item and all its variations
                    item_data["no_wear_skins"][unformmatted_name][
                        "tradeup_result_pool"
                    ] = data["items"][next_rarity]

                    for i in range(
                        skin_data["best_condition_index"],
                        skin_data["worst_condition_index"] + 1,
                    ):
                        condition = conditions[i].lower()
                        item_data["items"][condition + " " + unformmatted_name][
                            "tradeup_result_pool"
                        ] = data["items"][next_rarity]

                    if skin_data["has_stattrak_variant"]:
                        for i in range(
                            skin_data["best_condition_index"],
                            skin_data["worst_condition_index"] + 1,
                        ):
                            condition = conditions[i].lower()
                            item_data["items"][
                                "stattrak " + condition + " " + unformmatted_name
                            ]["tradeup_result_pool"] = data["items"][next_rarity]


# endregion


# Scrape all game data needed
def scrape_game_data():
    # === PART 1: Scrape the item data
    item_data = {"_id": "item_data", "items": {}, "no_wear_skins": {}}

    weapon_skin_links = []

    # get weapon skin links
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(get_links_from_page, weapon_skin_links),
            gun_endpoints + rare_item_endpoints,
        )

    # get weapon skin data
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(partial(scrape_weapon_skin_link, item_data), weapon_skin_links)

    # get weapon skin data
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(partial(scrape_sticker_page, item_data), sticker_endpoints)

    # === PART 2: Scrape containers and their data

    # weapon cases
    weapon_case_links = []
    get_links_from_page(weapon_case_links, weapon_case_endpoint)

    weapon_case_data = {}
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(scrape_case_link, weapon_case_data, item_data), weapon_case_links
        )

    # packages
    packages_links = [
        "https://csgoskins.gg/items/anubis-collection-package",
        "https://csgoskins.gg/items/x-ray-p250-package",
    ]
    packages_data = {}
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(scrape_package_link, packages_data, item_data, "package"),
            packages_links,
        )

    # souvenir packages
    souvenir_packages_links = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(get_links_from_page, souvenir_packages_links),
            souvenir_package_endpoints,
        )

    souvenir_packages_data = {}
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(
                scrape_package_link,
                souvenir_packages_data,
                item_data,
                "souvenir_package",
            ),
            souvenir_packages_links,
        )

    # sticker capsules
    sticker_capsules_links = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(get_links_from_page, sticker_capsules_links),
            sticker_capsule_endpoints,
        )

    sticker_capsules_data = {}
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(scrape_sticker_capsule_link, sticker_capsules_data),
            sticker_capsules_links,
        )

    container_data = {
        "_id": "container_data",
        **weapon_case_data,
        **packages_data,
        **souvenir_packages_data,
        **sticker_capsules_data,
    }

    set_tradeup_result_pools(item_data, container_data)

    return item_data, container_data


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
