"""
Copyright (C) 2022 William Redding - All Rights Reserved

A module containing commonly used string formatting and helper functions

Functions
~~~~~~~~~
* remove_skin_name_formatting
* currency_str_format
* round_sig_fig
* get_closest_match

See end of file for licence details
"""

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