# this is a script to generate the dictionary of items for each csgo container

from bs4 import BeautifulSoup
import requests
import json
from src.util.format import remove_skin_name_formatting

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
      "milspec": [],
      "restricted": [],
      "classified": [],
      "covert": [],
      "rare-item": []
    }

    #get gun skins
    link = f"https://csgostash.com/{container}"
    container_skins = requests.get(link)
    container_soup = BeautifulSoup(container_skins.content, "html.parser")

    container_name = remove_skin_name_formatting(
      container_soup.find("h1", {
        "class": "margin-top-sm"
      }).text)

    result_boxes = container_soup.find_all("div", {"class": "result-box"})

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
          quality = quality_div["class"][1].replace("color-", " ").strip()
          container_data[quality].append(name)

    #open rare-item skins and get them too if there are any
    if rare_items_link != None:
      rare_items_skins = requests.get(rare_items_link)
      rare_items_soup = BeautifulSoup(rare_items_skins.content, "html.parser")

      result_boxes = rare_items_soup.find_all("div", {"class": "result-box"})

      for result_box in result_boxes:
        h3 = result_box.find("h3")
        if h3 != None:
          unformatted_name = remove_skin_name_formatting(h3.text)
          if container_name not in unformatted_name: #avoids the link back to the cases original skins
            container_data["rare-item"].append(unformatted_name)
          

    result[container_name] = container_data
    print(f"Scraped {container_name}")

  with open("res/containers.json", "w+", encoding="utf-8") as file:
    json.dump(result, file, indent=4, ensure_ascii=False)