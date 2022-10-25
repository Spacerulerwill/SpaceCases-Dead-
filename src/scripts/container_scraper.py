# this is a script to generate the dictionary of items for each csgo container

from bs4 import BeautifulSoup
import requests
import json
from src.util.format import remove_skin_name_formatting
from re import sub
from decimal import Decimal

result = {}
container_endpoints = [
  "case/355/Recoil-Case", "case/339/Dreams-&-Nightmares-Case", 
  "case/321/Operation-Riptide-Case", "case/315/Snakebite-Case",
  "case/308/Operation-Broken-Fang-Case", "case/307/Fracture-Case",
  "case/303/Prisma-2-Case", "case/277/Shattered-Web-Case",
  "case/293/CS20-Case", "case/274/Prisma-Case", "case/38/Chroma-Case",
  "case/48/Chroma-2-Case", "case/141/Chroma-3-Case", "case/238/Clutch-Case",
  "case/1/CS:GO-Weapon-Case", "case/4/CS:GO-Weapon-Case-2", 
  "case/10/CS:GO-Weapon-Case-3", "case/259/Danger-Zone-Case",
  "case/2/eSports-2013-Case", "case/5/eSports-2013-Winter-Case",
  "case/19/eSports-2014-Summer-Case", "case/50/Falchion-Case",
  "case/144/Gamma-Case", "case/172/Gamma-2-Case", "case/179/Glove-Case",
"case/244/Horizon-Case", "case/17/Huntsman-Weapon-Case", "case/3/Operation-Bravo-Case",
  "case/18/Operation-Breakout-Weapon-Case", "case/208/Operation-Hydra-Case",
  "case/11/Operation-Phoenix-Weapon-Case", "case/29/Operation-Vanguard-Weapon-Case",
  "case/112/Operation-Wildfire-Case", "case/111/Revolver-Case", 
  "case/80/Shadow-Case", "case/207/Spectrum-Case", "case/220/Spectrum-2-Case",
  "case/7/Winter-Offensive-Weapon-Case"
]

def scrape_containers():
  for container in container_endpoints:

    container_data = {
      "items": {
        "milspec": [],
        "restricted": [],
        "classified": [],
        "covert": [],
        "rare items": []
      },
      "all items": []
    }

    #get gun skins
    link = f"https://csgostash.com/{container}"
    container_skins = requests.get(link)
    container_soup = BeautifulSoup(container_skins.content, "html.parser")

    #container name and image url
    container_name = container_soup.find("h1", {
        "class": "margin-top-sm"
      }).text

    price_div = container_soup.find("div", {"class": ["btn-group", "content-header-container-btn"]})
    container_price = price_div.find("a", {"class": ["btn", "btn-default", "market-button-item"]}).text

    container_price = container_price.split(" ")[0]
    container_price = sub(r'[^\d.]', '', container_price)
    container_data["price"] = int(Decimal(container_price) * 100)

    container_img_url = container_soup.find("a", {"class":"market-button-item"}).find("img")["src"]

    result_boxes = container_soup.find_all("div", {"class": "result-box"})
    result_boxes.reverse()

    rare_items_link = None

    for result_box in result_boxes:
      h3 = result_box.find("h3")

      if h3 != None:
        name = remove_skin_name_formatting(h3.text)

        if "gloves" in name:
          rare_items_link = link + "?Gloves=1"
        elif "knives" in name:
          rare_items_link = link + "?Knives=1"
        else:
          quality_div = result_box.find("div", {"class": "quality"})
          quality = quality_div["class"][1].replace("color-", " ").replace("-", "").strip()
          container_data["items"][quality].append(name)
          container_data["all items"].append(name)

    #open rare items skins and get them too if there are any
    if rare_items_link != None:
      rare_items_skins = requests.get(rare_items_link)
      rare_items_soup = BeautifulSoup(rare_items_skins.content, "html.parser")

      result_boxes = rare_items_soup.find_all("div", {"class": "result-box"})

      for result_box in result_boxes:
        h3 = result_box.find("h3")
        if h3 != None and "Case Skins" not in h3.text:
          unformatted_name = remove_skin_name_formatting(h3.text)
          if container_name not in unformatted_name: #avoids the link back to the cases original skins
            container_data["items"]["rare items"].append(unformatted_name)
            container_data["all items"].append(unformatted_name)

    container_data["formatted_name"] = container_name
    container_data["image_url"] = container_img_url
    result[remove_skin_name_formatting(container_name)] = container_data
    print(f"Scraped {container_name}")

  with open("res/containers.json", "w+", encoding="utf-8") as file:
    json.dump(result, file, indent=4, ensure_ascii=False)