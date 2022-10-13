from bs4 import BeautifulSoup
import requests
import json
from src.util.format import remove_skin_name_formatting

items = [
    # pistols
    "weapon/CZ75-Auto", "weapon/Desert+Eagle", "weapon/Dual+Berettas", "weapon/Five-SeveN", "weapon/Glock-18", "weapon/P2000", "weapon/P250", "weaponR8+Revolver",
     "weapon/Tec-9", "weapon/USP-S", 
    #rifles
    "weapon/AK-47", "weapon/AUG", "weapon/AWP", "weapon/FAMAS", "weapon/G3SG1", "weapon/Galil AR", "weapon/M4A1-S", "weapon/M4A4", "weapon/SCAR-20", "weapon/SG+553", "weapon/SSG+08",
    #smgs
    "weapon/MAC-10", "weapon/MP5-SD", "weapon/MP7", "weapon/MP9", "weapon/PP-Bizon", "weapon/P90", "weapon/UMP-45",
    #heavy
    "weapon/MAG-7", "weapon/Nova", "weapon/Sawed-Off", "weapon/XM1014", "weapon/M249", "weapon/Negev",

    #knives
    "weapon/Nomad+Knife", "weapon/Skeleton+Knife", "weapon/Survival+Knife", "weapon/Paracord+Knife", "weapon/Classic+Knife", 
    "weapon/Bayonet", "weapon/Bowie+Knife", "weapon/Butterfly+Knife", "weapon/Falchion+Knife",
    "weapon/Flip+Knife", "weapon/Gut+Knife", "weapon/Huntsman+Knife", "weapon/Karambit", "weapon/M9+Bayonet", 
    "weapon/Navaja+Knife", "weapon/Shadow+Daggers", "weapon/Stiletto+Knife", "weapon/Talon+Knife", "weapon/Ursus+Knife",

    #gloves
    "gloves?page=1", "gloves?page=2"
]

# skin floats and whether they are stattrak souvenir or none
def get_csgostash_static_data():

    result = {"_id": "csgostash_static_data"}

    for item in items:
        item_link = "https://csgostash.com/" + item
        page = requests.get(item_link)
        soup = BeautifulSoup(page.content, "html.parser")

        # get all result boxes (the boxes that have the skins in the)
        result_boxes = (soup.find_all("div", {"class": "result-box"}))
        for box in result_boxes:
                try:
                    #find link to skin in div
                    skin_link_div = box.find("div", {"class":"details-link"})
                    if skin_link_div != None:
                        skin_link = skin_link_div.find("a")["href"]
                        
                        page = requests.get(skin_link)
                        soup = BeautifulSoup(page.content, "html.parser")

                        formatted_name = soup.find("div", {"class": "result-box"}).find("h2").text
                        stattrak = soup.find("div", {"class": "stattrak"}) != None
                        souvenir = soup.find("div", {"class": "souvenir"}) != None
                        is_special = any(type in soup.find("div", {"class": "quality"}).text for type in ["Gloves", "Knife"])
                        
                        if "★ (Vanilla)" in formatted_name:
                            min_float = 0.0
                            max_float = 1.0
                        else:
                            markers = soup.find_all("div", {"class": "marker-value"})

                            min_float = float(markers[0].text)
                            max_float = float(markers[1].text)

                    skin_data = {"formatted_name": formatted_name, "min_float": min_float, "max_float": max_float, "stattrak": stattrak, "souvenir": souvenir, "is_special": is_special}

                    unformatted_name = remove_skin_name_formatting(formatted_name)

                    result[unformatted_name] = skin_data
                    
                    print(f"Scraped {formatted_name}")
                except:
                    pass

    with open("res/csgostash_static_data.json", "w+", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)


def dump_csgobackpack_api():
    data = requests.get("http://csgobackpack.net/api/GetItemsList/v2/").json()
    with open("res/csgobackpack_api.json", "w+", encoding="utf-8") as f:
        json.dump(data,f, indent=4, ensure_ascii=False)