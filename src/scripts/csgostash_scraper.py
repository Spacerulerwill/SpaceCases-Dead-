from bs4 import BeautifulSoup
import requests
import json

weapons = [
    # pistols
    "CZ75-Auto", "Desert Eagle", "Dual Berettas", "Five-SeveN", "Glock-18", "P2000", "P250", "R8 Revolver", "Tec-9", "USP-S", 
    #rifles
    "AK-47", "AUG", "AWP", "FAMAS", "G3SG1", "Galil AR", "M4A1-S", "M4A4", "SCAR-20", "SG 553", "SSG 08",
    #smgs
    "MAC-10", "MP5-SD", "MP7", "MP9", "PP-Bizon", "P90", "UMP-45",
    #heavy
    "MAG-7", "Nova", "Sawed-Off", "XM1014", "M249", "Negev",

    #knives
    "Nomad Knife", "Skeleton Knife", "Survival Knife", "Paracord Knife", "Classic Knife", "Bayonet", "Bowie Knife", "Butterfly Knife", "Falchion Knife",
    "Flip Knife", "Gut Knife", "Huntsman Knife", "Karambit", "M9 Bayonet", "Navaja Knife", "Shadow Daggers", "Stiletto Knife", "Talon Knife", "Ursus Knife"
]

# skin floats and whether they are stattrak souvenir or none
def get_csgostash_static_data():

    result = {"_id": "csgostash_static_data"}

    for weapon in weapons:
        weapon_link = "https://csgostash.com/weapon/" + weapon.replace(" ", "+")
        page = requests.get(weapon_link)
        soup = BeautifulSoup(page.content, "html.parser")

        # get all result boxes (the boxes that have the skins in the)
        result_boxes = (soup.find_all("div", {"class": "result-box"}))
        for box in result_boxes:
            h3 = box.find("h3") #skin name he3
            if h3 != None:
                skin_name = h3.text
                if "Default" not in skin_name:

                    #find link to skin in div
                    skin_link_div = box.find("div", {"class":"details-link"})
                    if skin_link_div != None:
                        skin_link = skin_link_div.find("a")["href"]
                        
                        page = requests.get(skin_link)
                        soup = BeautifulSoup(page.content, "html.parser")

                        stattrak = soup.find("div", {"class": "stattrak"}) != None
                        souvenir = soup.find("div", {"class": "souvenir"}) != None
                        is_special = any(type in soup.find("div", {"class": "quality"}).text for type in ["Gloves", "Knife"])
                        
                        if "★ (Vanilla)" in skin_name:
                            min_float = 0.0
                            max_float = 1.0
                        else:
                            markers = soup.find_all("div", {"class": "marker-value"})

                            min_float = markers[0].text
                            max_float = markers[1].text

                        skin_data = {"min_float": min_float, "max_float": max_float, "stattrak": stattrak, "souvenir": souvenir, "is_special": is_special}

                    if "★ (Vanilla)" in skin_name:
                        result[f"{weapon}"] = skin_data
                        print(f"Scraped {weapon}")
                    else:
                        result[f"{weapon} | {skin_name}"] = skin_data
                        print(f"Scraped {weapon} | {skin_name}")

    with open("res/csgostash_static_data.json", "w+") as file:
        json.dump(result, file, indent=4)


def dump_csgobackpack_api():
    data = requests.get("http://csgobackpack.net/api/GetItemsList/v2/").json()
    with open("res/csgobackpack_api.json", "w+") as f:
        json.dump(data,f, indent=4)


if __name__ == "__main__":
    dump_csgobackpack_api()
    #get_csgostash_static_data()