from decimal import Decimal
from typing import List
import Levenshtein
from urllib.parse import quote

#format skin names to a standardized formatt
def remove_skin_name_formatting(formatted_name:str) -> str:
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 "
    replace_chars = {
        "&": "and",
        "-": " ",
        "ö": "o"
    }

    unformatted_name = formatted_name.lower() #lowercase
    for char,replace in replace_chars.items(): #replacements
        unformatted_name = unformatted_name.replace(char, replace)
    unformatted_name = ''.join(ch for ch in unformatted_name if ch in allowed_chars).strip() #only allowed chars
    unformatted_name = " ".join(unformatted_name.split()) # remove doubles spaces
    return unformatted_name

#format currency integers to strings e.g 10000 = $100.00
def currency_str_format(amount:int) -> str:
    return "$" + str((Decimal(amount) / 100).quantize(Decimal('0.01')))

#round a float to a specified number on significant figures
def round_sig_fig(number:float, sig_figs:int) -> float:
    return '{:g}'.format(float('{:.{p}g}'.format(number, p=sig_figs)))

# get closest match to query using levenstein ratio from list of options
def get_closest_match(query:str, options:List[str], threshold:float=0.8) -> str | None:
    highest_ratio = 0
    closest_match = None
    for option in options:
        ratio = Levenshtein.ratio(query, option)
        if ratio > highest_ratio and ratio > threshold:
            highest_ratio = ratio
            closest_match = option
    
    return closest_match

def get_inspect_link_3D(steam_inspect_link:str) -> str:
    return "https://skinbaron.de/en/3dviewer?inspectLink=" + quote(steam_inspect_link)

