"""
Webscraper script used to scrape all the containers items and container prices
"""

from bs4 import BeautifulSoup
import concurrent.futures
import requests
from functools import partial
from src.util.string_util import remove_skin_name_formatting
from src.util.constants import MAX_THREADS
from re import sub
from decimal import Decimal
from timeit import default_timer as timer
from datetime import timedelta

NO_PRICE_FOUND = 100000

collection_endpoints = [
    "https://csgostash.com/collection/The+Vertigo+Collection",
    "https://csgostash.com/collection/The+Train+Collection",
    "https://csgostash.com/collection/The+St.+Marc+Collection",
    "https://csgostash.com/collection/The+Safehouse+Collection",
    "https://csgostash.com/collection/The+Rising+Sun+Collection",
    "https://csgostash.com/collection/The+Overpass+Collection",
    "https://csgostash.com/collection/The+Office+Collection",
    "https://csgostash.com/collection/The+Nuke+Collection",
    "https://csgostash.com/collection/The+Norse+Collection",
    "https://csgostash.com/collection/The+Mirage+Collection",
    "https://csgostash.com/collection/The+Militia+Collection",
    "https://csgostash.com/collection/The+Lake+Collection",
    "https://csgostash.com/collection/The+Italy+Collection",
    "https://csgostash.com/collection/The+Inferno+Collection",
    "https://csgostash.com/collection/The+Havoc+Collection",
    "https://csgostash.com/collection/The+Gods+and+Monsters+Collection",
    "https://csgostash.com/collection/The+Dust+2+Collection",
    "https://csgostash.com/collection/The+Dust+Collection",
    "https://csgostash.com/collection/The+Control+Collection",
    "https://csgostash.com/collection/The+Cobblestone+Collection",
    "https://csgostash.com/collection/The+Chop+Shop+Collection",
    "https://csgostash.com/collection/The+Canals+Collection",
    "https://csgostash.com/collection/The+Cache+Collection",
    "https://csgostash.com/collection/The+Blacksite+Collection",
    "https://csgostash.com/collection/The+Bank+Collection",
    "https://csgostash.com/collection/The+Baggage+Collection",
    "https://csgostash.com/collection/The+Aztec+Collection",
    "https://csgostash.com/collection/The+Assault+Collection",
    "https://csgostash.com/collection/The+Ancient+Collection",
    "https://csgostash.com/collection/The+Alpha+Collection",
    "https://csgostash.com/collection/The+2018+Nuke+Collection",
    "https://csgostash.com/collection/The+2018+Inferno+Collection",
    "https://csgostash.com/collection/The+2021+Vertigo+Collection",
    "https://csgostash.com/collection/The+2021+Dust+2+Collection",
    "https://csgostash.com/collection/The+2021+Mirage+Collection",
    "https://csgostash.com/collection/The+2021+Train+Collection",
]

container_endpoints = [
    "https://csgostash.com/case/376/Revolution-Case",
    "https://csgostash.com/case/355/Recoil-Case",
    "https://csgostash.com/case/339/Dreams-&-Nightmares-Case",
    "https://csgostash.com/case/321/Operation-Riptide-Case",
    "https://csgostash.com/case/315/Snakebite-Case",
    "https://csgostash.com/case/308/Operation-Broken-Fang-Case",
    "https://csgostash.com/case/307/Fracture-Case",
    "https://csgostash.com/case/303/Prisma-2-Case",
    "https://csgostash.com/case/277/Shattered-Web-Case",
    "https://csgostash.com/case/293/CS20-Case",
    "https://csgostash.com/case/274/Prisma-Case",
    "https://csgostash.com/case/38/Chroma-Case",
    "https://csgostash.com/case/48/Chroma-2-Case",
    "https://csgostash.com/case/141/Chroma-3-Case",
    "https://csgostash.com/case/238/Clutch-Case",
    "https://csgostash.com/case/1/CS:GO-Weapon-Case",
    "https://csgostash.com/case/4/CS:GO-Weapon-Case-2",
    "https://csgostash.com/case/10/CS:GO-Weapon-Case-3",
    "https://csgostash.com/case/259/Danger-Zone-Case",
    "https://csgostash.com/case/2/eSports-2013-Case",
    "https://csgostash.com/case/5/eSports-2013-Winter-Case",
    "https://csgostash.com/case/19/eSports-2014-Summer-Case",
    "https://csgostash.com/case/50/Falchion-Case",
    "https://csgostash.com/case/144/Gamma-Case",
    "https://csgostash.com/case/172/Gamma-2-Case",
    "https://csgostash.com/case/179/Glove-Case",
    "https://csgostash.com/case/244/Horizon-Case",
    "https://csgostash.com/case/17/Huntsman-Weapon-Case",
    "https://csgostash.com/case/3/Operation-Bravo-Case",
    "https://csgostash.com/case/18/Operation-Breakout-Weapon-Case",
    "https://csgostash.com/case/208/Operation-Hydra-Case",
    "https://csgostash.com/case/11/Operation-Phoenix-Weapon-Case",
    "https://csgostash.com/case/29/Operation-Vanguard-Weapon-Case",
    "https://csgostash.com/case/112/Operation-Wildfire-Case",
    "https://csgostash.com/case/111/Revolver-Case",
    "https://csgostash.com/case/80/Shadow-Case",
    "https://csgostash.com/case/207/Spectrum-Case",
    "https://csgostash.com/case/220/Spectrum-2-Case",
    "https://csgostash.com/case/7/Winter-Offensive-Weapon-Case",
]

souvenir_package_endpoints = {
    "https://csgostash.com/containers/souvenir-packages",
    "https://csgostash.com/containers/souvenir-packages?page=2",
    "https://csgostash.com/containers/souvenir-packages?page=3",
}

def calculate_container_odds(items_dict:dict) -> dict:
    # find all rarities that have actual item data
    rarities_with_items = [rarity for rarity, items in items_dict.items() if len(items) != 0]

    # the most common is 80%, each rarity above is 5 times less likely
    rarity_odds = {rarity: 0.8 * 0.2**count for count, rarity in enumerate(rarities_with_items)}

    # sum of series: 0.8 * 0.2**X does not equal 1, therefore we must make them total one to avoid any boundry cases
    sum_odds = sum(rarity_odds.values()) 
    add_to_each = (1 - sum_odds) / len(rarities_with_items)

    rarity_odds = {rarity: odd + add_to_each for rarity, odd in rarity_odds.items()}

    final_rarity_odds = {}

    odds = list(rarity_odds.values())
    for count, rarity in enumerate(rarity_odds.keys()):
        final_rarity_odds[rarity] = sum(odds[0:count])

    # reverse dict
    return dict(reversed(final_rarity_odds.items()))


def scrape_container(result, container_link):
    container_data = {
        "type": "case",
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

    # get gun skins
    container_skins = requests.get(container_link)
    container_soup = BeautifulSoup(container_skins.content, "html.parser")

    # container name and image url
    container_name = (
        container_soup.find("div", {"class": ["inline-middle collapsed-top-margin"]})
        .find("h1")
        .text
    )

    # remove punctuation
    container_name = container_name.replace("&", "and")
    container_name = sub("[^\w\s]", "", container_name)

    price_div = container_soup.find(
        "div", {"class": ["btn-group", "content-header-container-btn"]}
    )
    container_price = price_div.find(
        "a", {"class": ["btn", "btn-default", "market-button-item"]}
    ).text

    container_price = container_price.split(" ")[0]
    container_price = sub(r"[^\d.]", "", container_price)
    container_data["price"] = int(Decimal(container_price) * 100)

    container_img_url = container_soup.find("a", {"class": "market-button-item"}).find(
        "img"
    )["src"]

    result_boxes = container_soup.find_all("div", {"class": "result-box"})
    result_boxes.reverse()

    rare_items_link = None

    for result_box in result_boxes:
        h3 = result_box.find("h3")

        if h3 != None:
            name = remove_skin_name_formatting(h3.text)

            if "gloves" in name:
                rare_items_link = container_link + "?Gloves=1"
            elif "knives" in name:
                rare_items_link = container_link + "?Knives=1"
            else:
                quality_div = result_box.find("div", {"class": "quality"})
                quality = (
                    quality_div["class"][1]
                    .replace("color-", " ")
                    .replace("-", "")
                    .strip()
                )
                container_data["items"][quality].append(name)
                container_data["all items"].append(name)

    # open rare items skins and get them too if there are any
    if rare_items_link != None:
        rare_items_skins = requests.get(rare_items_link)
        rare_items_soup = BeautifulSoup(rare_items_skins.content, "html.parser")

        result_boxes = rare_items_soup.find_all("div", {"class": "result-box"})

        for result_box in result_boxes:
            h3 = result_box.find("h3")
            if h3 != None and "Case Skins" not in h3.text:
                unformatted_name = remove_skin_name_formatting(h3.text)
                if (
                    container_name not in unformatted_name
                ):  # avoids the link back to the cases original skins
                    container_data["items"]["rare items"].append(unformatted_name)
                    container_data["all items"].append(unformatted_name)

    container_data["formatted_name"] = container_name
    container_data["image_url"] = container_img_url
    container_data["odds"] = calculate_container_odds(container_data["items"]) 
    result[remove_skin_name_formatting(container_name)] = container_data


def scrape_collection(collections, collection_link):
    collection_data = {
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

    html = requests.get(collection_link)
    soup = BeautifulSoup(html.content, "html.parser")

    # container name and image url
    collection_name = (
        soup.find("div", {"class": ["inline-middle collapsed-top-margin"]})
        .find("h1")
        .text.lower()
    )

    result_boxes = soup.find_all("div", {"class": "result-box"})
    for result_box in result_boxes:
        h3 = result_box.find("h3")
        if h3 != None:
            name = remove_skin_name_formatting(h3.text)

            quality_div = result_box.find("div", {"class": "quality"})
            quality = (
                quality_div["class"][1].replace("color-", " ").replace("-", "").strip()
            )
            collection_data["items"][quality].append(name)
            collection_data["all items"].append(name)

    collections[collection_name] = collection_data


def scrape_souvenir_package(collections: dict, souvenir_data: dict, link: str):
    html = requests.get(link)
    soup = BeautifulSoup(html.content, "html.parser")

    package_boxes = soup.select("div.well.result-box.nomargin")
    for box in package_boxes:
        h4 = box.find("h4")
        if h4 is None:
            continue

        pkg_name = h4.text
        unformatted_pkg_name = pkg_name.lower()
        collection_name = (
            box.find("div", {"class": "containers-details-link"}).text.lower().strip()
        )
        collection_data = collections[collection_name]
        image_url = box.find("img", {"class": "img-responsive"})["src"]
        price_str = box.find("div", {"class": "price"}).text.strip()

        if price_str != "No Recent Price":
            price_str = sub(r"[^\d.]", "", price_str)
            price = int(Decimal(price_str) * 100)
        else:
            price = NO_PRICE_FOUND

        pkg_data = {
            "type": "souvenir_package",
            "items": collection_data["items"],
            "all items": collection_data["all items"],
            "formatted_name": pkg_name,
            "image_url": image_url,
            "price": price,
            "odds": calculate_container_odds(collection_data["items"])
        }

        souvenir_data[unformatted_pkg_name] = pkg_data


def collection_scrape() -> dict:
    # scrape collections
    start = timer()

    print("Scraping collection data...")
    collections = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(partial(scrape_collection, collections), collection_endpoints)

    end = timer()
    print(f"Executed in {timedelta(seconds=end-start)}")
    return collections


def souvenir_package_scrape(collections: dict) -> dict:
    start = timer()

    # scrape souvenir packages
    print("Scraping souvenir packages...")
    souvenir_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(scrape_souvenir_package, collections, souvenir_data),
            souvenir_package_endpoints,
        )

    end = timer()
    print(f"Executed in {timedelta(seconds=end-start)}")

    return souvenir_data


def case_scrape() -> dict:
    start = timer()

    # scrape containers
    print("Scraping case data...")
    case_data = {"_id": "container-data"}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(partial(scrape_container, case_data), container_endpoints)

    end = timer()
    print(f"Executed in {timedelta(seconds=end-start)}")

    return case_data
