from decimal import Decimal
from typing import List
import Levenshtein
from urllib.parse import quote


def remove_skin_name_formatting(formatted_name: str) -> str:
    """Remove formatting from a skin name

    Args:
        formatted_namea: the sin name
    Returns:
        the skin name with no formatting
    Examples:
        StatTrak™ Factory New AWP | Phobos -> stattrak factory new awp phobos
    """
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 "
    replace_chars = {"&": "and", "-": " ", "ö": "o"}

    unformatted_name = formatted_name.lower()  # lowercase
    for char, replace in replace_chars.items():  # replacements
        unformatted_name = unformatted_name.replace(char, replace)
    unformatted_name = "".join(
        ch for ch in unformatted_name if ch in allowed_chars
    ).strip()  # only allowed chars
    unformatted_name = " ".join(unformatted_name.split())  # remove doubles spaces
    return unformatted_name


def currency_str_format(amount: int) -> str:
    """Convert an integer to a currency string

    Args:
        amount: the number of cents.
    Returns:
        a string formatted as a currency string.
    Examples:
        10000 -> "$100.00"
    """
    return "$" + str((Decimal(amount) / 100).quantize(Decimal("0.01")))


def round_sig_fig(number: float, sig_figs: int) -> str:
    """Round a float to a number of significant figures as a string

    Args:
        number: the float
        sig_figs: the number of significant figures
    Returns:
        a string formatted as a currency string.
    Examples:
        103.546, 3 -> "104"
    """
    return "{:g}".format(float("{:.{p}g}".format(number, p=sig_figs)))


def get_closest_match(
    query: str, options: List[str], threshold: float = 0.8
) -> str | None:
    """Return the closest match to a string given a list of strings.

    Args:
        query: the string
        options: list of options to match the string against
        threshold: the error margin
    Returns:
        the matched option if one is found
        None if no option is found
    """
    highest_ratio = 0
    closest_match = None
    for option in options:
        ratio = Levenshtein.ratio(query, option)
        if ratio > highest_ratio and ratio > threshold:
            highest_ratio = ratio
            closest_match = option

    return closest_match


# get skin baron inspect link
def get_inspect_link_3D(steam_inspect_link: str) -> str:
    """Convert steam inspect link to skinbaron 3D inspect link"""
    return "https://skinbaron.de/en/3dviewer?inspectLink=" + quote(steam_inspect_link)