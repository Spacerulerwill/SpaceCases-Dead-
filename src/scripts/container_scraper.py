"""
Webscraper script used to scrape all the containers items and container prices
"""

import re
from bs4 import BeautifulSoup
import concurrent.futures
import requests
from functools import partial
from src.util.string_util import remove_skin_name_formatting
from src.util.constants import MAX_THREADS, HTTP_HEADERS
from re import sub
from decimal import Decimal
from timeit import default_timer as timer
from datetime import timedelta

NO_PRICE_FOUND = 300000
NO_PRICE_FOUND_STICKER_CAPSULE = 100000

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

souvenir_package_endpoints = [
    "https://csgostash.com/containers/souvenir-packages",
    "https://csgostash.com/containers/souvenir-packages?page=2",
    "https://csgostash.com/containers/souvenir-packages?page=3",
]

sticker_capsule_endpoints = [
    # sticker capsules
    "https://csgostash.com/stickers/capsule/375/Espionage-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/361/Rio-2022-Contenders-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/360/Rio-2022-Challengers-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/359/Rio-2022-Legends-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/356/10-Year-Birthday-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/343/Antwerp-2022-Contenders-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/342/Antwerp-2022-Challengers-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/341/Antwerp-2022-Legends-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/340/The-Boardroom-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/326/Stockholm-2021-Contenders-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/325/Stockholm-2021-Challengers-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/324/Stockholm-2021-Legends-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/320/Battlefield-2042-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/319/2021-Community-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/314/Poorly-Drawn-Capsule",
    "https://csgostash.com/stickers/capsule/313/2020-RMR-Contenders",
    "https://csgostash.com/stickers/capsule/312/2020-RMR-Challengers",
    "https://csgostash.com/stickers/capsule/311/2020-RMR-Legends",
    "https://csgostash.com/stickers/capsule/306/Warhammer-40-000-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/301/Half-Life:-Alyx-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/295/Halo-Capsule",
    "https://csgostash.com/stickers/capsule/294/CS20-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/280/Berlin-2019-Minor-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/279/Berlin-2019-Returning-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/278/Berlin-2019-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/276/Chicken-Capsule",
    "https://csgostash.com/stickers/capsule/275/Feral-Predators-Capsule",
    "https://csgostash.com/stickers/capsule/262/Katowice-2019-Minor-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/261/Katowice-2019-Returning-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/260/Katowice-2019-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/258/Skill-Groups-Capsule",
    "https://csgostash.com/stickers/capsule/247/London-2018-Minor-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/246/London-2018-Returning-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/245/London-2018-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/241/Boston-2018-Attending-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/239/Boston-2018-Minor-Challengers-with-Flash-Gaming-Holo-Foil",
    "https://csgostash.com/stickers/capsule/237/Community-Capsule-2018",
    "https://csgostash.com/stickers/capsule/226/Boston-2018-Minor-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/225/Boston-2018-Returning-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/224/Boston-2018-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/222/Perfect-World-Sticker-Capsule-2",
    "https://csgostash.com/stickers/capsule/221/Perfect-World-Sticker-Capsule-1",
    "https://csgostash.com/stickers/capsule/210/Krakow-2017-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/209/Krakow-2017-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/181/Atlanta-2017-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/180/Atlanta-2017-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/174/Bestiary-Capsule",
    "https://csgostash.com/stickers/capsule/173/Sugarface-Capsule",
    "https://csgostash.com/stickers/capsule/146/Cologne-2016-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/145/Cologne-2016-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/114/MLG-Columbus-2016-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/113/MLG-Columbus-2016-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/110/Team-Roles-Capsule",
    "https://csgostash.com/stickers/capsule/109/Slid3-Capsule",
    "https://csgostash.com/stickers/capsule/108/Pinups-Capsule",
    "https://csgostash.com/stickers/capsule/82/DreamHack-Cluj-Napoca-2015-Challengers-Foil",
    "https://csgostash.com/stickers/capsule/81/DreamHack-Cluj-Napoca-2015-Legends-Foil",
    "https://csgostash.com/stickers/capsule/52/ESL-One-Cologne-2015-Challengers-Foil",
    "https://csgostash.com/stickers/capsule/51/ESL-One-Cologne-2015-Legends-Foil",
    "https://csgostash.com/stickers/capsule/49/Enfu-Sticker-Capsule",
    "https://csgostash.com/stickers/capsule/47/ESL-One-Katowice-2015-Challengers-Holo-Foil",
    "https://csgostash.com/stickers/capsule/46/ESL-One-Katowice-2015-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/30/DreamHack-2014-Legends-Holo-Foil",
    "https://csgostash.com/stickers/capsule/21/ESL-One-Cologne-2014-Challengers",
    "https://csgostash.com/stickers/capsule/20/ESL-One-Cologne-2014-Legends",
    "https://csgostash.com/stickers/capsule/16/Community-Sticker-Capsule-1",
    "https://csgostash.com/stickers/capsule/15/EMS-Katowice-2014-Legends",
    "https://csgostash.com/stickers/capsule/14/EMS-Katowice-2014-Challengers",
    "https://csgostash.com/stickers/capsule/12/Sticker-Capsule-2",
    "https://csgostash.com/stickers/capsule/9/Sticker-Capsule",
    # autograph capsules
    "https://csgostash.com/stickers/capsule/372/Rio-2022-Champions-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/371/Rio-2022-Contenders-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/370/Rio-2022-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/369/Rio-2022-Legends-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/354/Antwerp-2022-Champions-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/353/Antwerp-2022-Contenders-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/352/Antwerp-2022-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/351/Antwerp-2022-Legends-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/338/Stockholm-2021-Finalists-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/337/Stockholm-2021-Champions-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/283/Berlin-2019-Minor-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/282/Berlin-2019-Returning-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/281/Berlin-2019-Legends-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/265/Katowice-2019-Minor-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/264/Katowice-2019-Returning-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/263/Katowice-2019-Legends-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/250/London-2018-Minor-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/249/London-2018-Returning-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/248/London-2018-Legends-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/242/Boston-2018-Attending-Legends-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/240/Boston-2018-Minor-Challengers-with-Flash-Gaming-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/229/Boston-2018-Minor-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/228/Boston-2018-Returning-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/227/Boston-2018-Legends-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/212/Krakow-2017-Legends-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/211/Krakow-2017-Challengers-Autograph-Capsule",
    "https://csgostash.com/stickers/capsule/199/Autograph-Capsule-VirtusPro-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/198/Autograph-Capsule-Team-Liquid-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/197/Autograph-Capsule-SK-Gaming-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/196/Autograph-Capsule-OpTic-Gaming-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/195/Autograph-Capsule-North-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/194/Autograph-Capsule-Natus-Vincere-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/193/Autograph-Capsule-mousesports-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/192/Autograph-Capsule-HellRaisers-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/191/Autograph-Capsule-GODSENT-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/190/Autograph-Capsule-Gambit-Gaming-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/189/Autograph-Capsule-G2-Esports-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/188/Autograph-Capsule-Fnatic-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/187/Autograph-Capsule-Flipsid3-Tactics-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/186/Autograph-Capsule-FaZe-Clan-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/185/Autograph-Capsule-Team-EnVyUs-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/184/Autograph-Capsule-Astralis-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/183/Autograph-Capsule-Legends-Foil-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/182/Autograph-Capsule-Challengers-Foil-Atlanta-2017",
    "https://csgostash.com/stickers/capsule/164/Autograph-Capsule-Team-Dignitas-Cologne-2016",
    "https://csgostash.com/stickers/capsule/163/Autograph-Capsule-Fnatic-Cologne-2016",
    "https://csgostash.com/stickers/capsule/162/Autograph-Capsule-Team-EnVyUs-Cologne-2016",
    "https://csgostash.com/stickers/capsule/161/Autograph-Capsule-Astralis-Cologne-2016",
    "https://csgostash.com/stickers/capsule/160/Autograph-Capsule-FaZe-Clan-Cologne-2016",
    "https://csgostash.com/stickers/capsule/159/Autograph-Capsule-G2-Esports-Cologne-2016",
    "https://csgostash.com/stickers/capsule/158/Autograph-Capsule-SK-Gaming-Cologne-2016",
    "https://csgostash.com/stickers/capsule/157/Autograph-Capsule-VirtusPro-Cologne-2016",
    "https://csgostash.com/stickers/capsule/156/Autograph-Capsule-Natus-Vincere-Cologne-2016",
    "https://csgostash.com/stickers/capsule/155/Autograph-Capsule-mousesports-Cologne-2016",
    "https://csgostash.com/stickers/capsule/154/Autograph-Capsule-Team-Liquid-Cologne-2016",
    "https://csgostash.com/stickers/capsule/153/Autograph-Capsule-Flipsid3-Tactics-Cologne-2016",
    "https://csgostash.com/stickers/capsule/152/Autograph-Capsule-Gambit-Gaming-Cologne-2016",
    "https://csgostash.com/stickers/capsule/151/Autograph-Capsule-Counter-Logic-Gaming-Cologne-2016",
    "https://csgostash.com/stickers/capsule/150/Autograph-Capsule-OpTic-Gaming-Cologne-2016",
    "https://csgostash.com/stickers/capsule/149/Autograph-Capsule-Ninjas-in-Pyjamas-Cologne-2016",
    "https://csgostash.com/stickers/capsule/148/Autograph-Capsule-Legends-Foil-Cologne-2016",
    "https://csgostash.com/stickers/capsule/147/Autograph-Capsule-Challengers-Foil-Cologne-2016",
    "https://csgostash.com/stickers/capsule/132/Autograph-Capsule-Luminosity-Gaming-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/131/Autograph-Capsule-Fnatic-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/130/Autograph-Capsule-Team-EnVyUs-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/129/Autograph-Capsule-Astralis-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/128/Autograph-Capsule-FaZe-Clan-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/127/Autograph-Capsule-G2-Esports-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/126/Autograph-Capsule-Cloud9-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/125/Autograph-Capsule-VirtusPro-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/124/Autograph-Capsule-Natus-Vincere-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/123/Autograph-Capsule-mousesports-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/122/Autograph-Capsule-Team-Liquid-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/121/Autograph-Capsule-Flipsid3-Tactics-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/120/Autograph-Capsule-Gambit-Gaming-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/119/Autograph-Capsule-Counter-Logic-Gaming-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/118/Autograph-Capsule-Splyce-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/117/Autograph-Capsule-Ninjas-in-Pyjamas-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/116/Autograph-Capsule-Legends-Foil-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/115/Autograph-Capsule-Challengers-Foil-MLG-Columbus-2016",
    "https://csgostash.com/stickers/capsule/100/Autograph-Capsule-Luminosity-Gaming-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/99/Autograph-Capsule-Fnatic-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/98/Autograph-Capsule-Team-EnVyUs-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/97/Autograph-Capsule-Team-SoloMid-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/96/Autograph-Capsule-Titan-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/95/Autograph-Capsule-G2-Esports-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/94/Autograph-Capsule-Cloud9-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/93/Autograph-Capsule-VirtusPro-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/92/Autograph-Capsule-Natus-Vincere-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/91/Autograph-Capsule-mousesports-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/90/Autograph-Capsule-Team-Liquid-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/89/Autograph-Capsule-Flipsid3-Tactics-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/88/Autograph-Capsule-Vexed-Gaming-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/87/Autograph-Capsule-Counter-Logic-Gaming-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/86/Autograph-Capsule-Team-Dignitas-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/85/Autograph-Capsule-Ninjas-in-Pyjamas-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/84/Autograph-Capsule-Legends-Foil-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/83/Autograph-Capsule-Challengers-Foil-Cluj-Napoca-2015",
    "https://csgostash.com/stickers/capsule/72/Autograph-Capsule-Cloud9-G2A-Cologne-2015",
    "https://csgostash.com/stickers/capsule/71/Autograph-Capsule-Counter-Logic-Gaming-Cologne-2015",
    "https://csgostash.com/stickers/capsule/70/Autograph-Capsule-Flipsid3-Tactics-Cologne-2015",
    "https://csgostash.com/stickers/capsule/69/Autograph-Capsule-Team-Kinguin-Cologne-2015",
    "https://csgostash.com/stickers/capsule/68/Autograph-Capsule-Team-eBettle-Cologne-2015",
    "https://csgostash.com/stickers/capsule/67/Autograph-Capsule-Team-Immunity-Cologne-2015",
    "https://csgostash.com/stickers/capsule/66/Autograph-Capsule-Renegades-Cologne-2015",
    "https://csgostash.com/stickers/capsule/65/Autograph-Capsule-mousesports-Cologne-2015",
    "https://csgostash.com/stickers/capsule/64/Autograph-Capsule-VirtusPro-Cologne-2015",
    "https://csgostash.com/stickers/capsule/63/Autograph-Capsule-Team-SoloMid-Cologne-2015",
    "https://csgostash.com/stickers/capsule/62/Autograph-Capsule-Titan-Cologne-2015",
    "https://csgostash.com/stickers/capsule/61/Autograph-Capsule-Team-EnVyUs-Cologne-2015",
    "https://csgostash.com/stickers/capsule/60/Autograph-Capsule-Ninjas-in-Pyjamas-Cologne-2015",
    "https://csgostash.com/stickers/capsule/59/Autograph-Capsule-Natus-Vincere-Cologne-2015",
    "https://csgostash.com/stickers/capsule/58/Autograph-Capsule-Luminosity-Gaming-Cologne-2015",
    "https://csgostash.com/stickers/capsule/57/Autograph-Capsule-Fnatic-Cologne-2015",
    "https://csgostash.com/stickers/capsule/56/Autograph-Capsule-Group-D-Foil-Cologne-2015",
    "https://csgostash.com/stickers/capsule/55/Autograph-Capsule-Group-C-Foil-Cologne-2015",
    "https://csgostash.com/stickers/capsule/54/Autograph-Capsule-Group-B-Foil-Cologne-2015",
    "https://csgostash.com/stickers/capsule/53/Autograph-Capsule-Group-A-Foil-Cologne-2015",
]


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
    container_skins = requests.get(container_link, headers=HTTP_HEADERS)
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
        rare_items_skins = requests.get(rare_items_link, headers=HTTP_HEADERS)
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

    # remove any rarities without items
    container_data["items"] = {
        rarity: items
        for rarity, items in container_data["items"].items()
        if len(items) != 0
    }
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

    html = requests.get(collection_link, headers=HTTP_HEADERS)
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
    html = requests.get(link, headers=HTTP_HEADERS)
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
            "items": {
                rarity: items
                for rarity, items in collection_data["items"].items()
                if len(items) != 0
            },  # remove rarities without items in them
            "all items": collection_data["all items"],
            "formatted_name": pkg_name,
            "image_url": image_url,
            "price": price,
            "odds": calculate_container_odds(collection_data["items"]),
        }

        souvenir_data[unformatted_pkg_name] = pkg_data


sticker_modifiers = ["foil", "gold", "holo", "glitter", "lenticular"]


def get_items_from_sticker_soup(
    all_items_list: list, items_dict: dict, soup: BeautifulSoup
):
    result_boxes = soup.select("div.well.result-box.nomargin")

    for result_box in result_boxes:
        h3 = result_box.find("h3")

        if h3 is None:
            continue

        formatted_sticker_name = h3.text.strip()
        formatted_tournament_name = result_box.find("h4")

        # any((modifier := mod) in formatted_sticker_name for mod in sticker_modifiers)

        if formatted_tournament_name is not None:
            formatted_tournament_name = formatted_tournament_name.find("a").text.strip()
            formatted_sticker_name = (
                f"{formatted_sticker_name} | {formatted_tournament_name}"
            )

        unformatted_sticker_name = remove_skin_name_formatting(formatted_sticker_name)

        rarity = (
            result_box.find("div", {"class": "quality"})
            .text.split(" ")[0]
            .lower()
            .strip()
        )

        items_dict[rarity].append(unformatted_sticker_name)
        all_items_list.append(unformatted_sticker_name)


def scrape_sticker_capsule(sticker_capsule_data: dict, link: str):
    try:
        html = requests.get(link, headers=HTTP_HEADERS)
        soup = BeautifulSoup(html.content, "html.parser")

        formatted_name = soup.find("h1", {"class": "margin-top-sm"}).text.strip()

        # format unformatted name
        # remove (Foil), (Holo/Foil) etc, strip and remove double spaces that result
        unformatted_name = remove_skin_name_formatting(formatted_name)

        for remove in ["holo", "foil", "holofoil"]:
            unformatted_name = unformatted_name.replace(remove, "")

        unformatted_name = unformatted_name.strip()
        unformatted_name = " ".join(unformatted_name.split())

        image_url = soup.select_one(
            "img.img-responsive.center-block.content-header-img-margin"
        )["src"]

        price_div = soup.select_one("div.btn-group.content-header-container-btn")
        price_str = price_div.find("a").text

        if price_str == "No Recent Price on Steam":
            price = NO_PRICE_FOUND_STICKER_CAPSULE
        else:
            price = int(re.sub("[^0-9]", "", price_str))

        page_selector = soup.find("ul", {"class": "pagination"})

        items_dict = {
            "high": [],
            "remarkable": [],
            "exotic": [],
            "extraordinary": [],
            "contraband": [],
        }

        all_items = []

        # get items from first page
        get_items_from_sticker_soup(all_items, items_dict, soup)

        if page_selector is not None:
            # if multiple pages, scrape all of them
            pages = len(page_selector.find_all("li")) - 2

            for i in range(1, pages):
                html = requests.get(f"{link}?page={i+1}", headers=HTTP_HEADERS)
                soup = BeautifulSoup(html.content, "html.parser")
                get_items_from_sticker_soup(all_items, items_dict, soup)

        # remove empty keys from items_dict
        items_dict = {rarity: items for rarity, items in items_dict.items() if items}

        sticker_capsule_data[unformatted_name] = {
            "type": "sticker_capsule",
            "formatted_name": formatted_name,
            "image_url": image_url,
            "price": price,
            "items": items_dict,
            "all items": all_items,
            "odds": calculate_container_odds(items_dict),
        }

    except Exception as e:
        pass
        # print(e)


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
    case_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(partial(scrape_container, case_data), container_endpoints)

    end = timer()
    print(f"Executed in {timedelta(seconds=end-start)}")

    return case_data


def sticker_capsule_scrape() -> dict:
    start = timer()

    # scrape containers
    print("Scraping sticker capsules data...")
    sticker_capsule_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.map(
            partial(scrape_sticker_capsule, sticker_capsule_data),
            sticker_capsule_endpoints,
        )

    end = timer()
    print(f"Executed in {timedelta(seconds=end-start)}")

    return sticker_capsule_data
