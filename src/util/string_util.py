"""
Copyright (C) 2022 William Redding - All Rights Reserved

A module containing commonly used string formatting and helper functions

Functions
~~~~~~~~~
* remove_skin_name_formatting
* currency_str_format
* round_sig_fig
* get_closest_match
* get_inspect_link_3D

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


# get skin baron inspect link
def get_inspect_link_3D(steam_inspect_link: str) -> str:
    """Convert steam inspect link to skinbaron 3D inspect link"""
    return "https://skinbaron.de/en/3dviewer?inspectLink=" + quote(steam_inspect_link)


"""
                    GNU GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU General Public License is a free, copyleft license for
software and other kinds of works.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
the GNU General Public License is intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.  We, the Free Software Foundation, use the
GNU General Public License for most of our software; it applies also to
any other work released this way by its authors.  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must pass on to the recipients the same
freedoms that you received.  You must make sure that they, too, receive
or can get the source code.  And you must show them these terms so they
know their rights.

  Developers that use the GNU GPL protect your rights with two steps:
(1) assert copyright on the software, and (2) offer you this License
giving you legal permission to copy, distribute and/or modify it.

  For the developers' and authors' protection, the GPL clearly explains
that there is no warranty for this free software.  For both users' and
authors' sake, the GPL requires that modified versions be marked as
changed, so that their problems will not be attributed erroneously to
authors of previous versions.

  Some devices are designed to deny users access to install or run
modified versions of the software inside them, although the manufacturer
can do so.  This is fundamentally incompatible with the aim of
protecting users' freedom to change the software.  The systematic
pattern of such abuse occurs in the area of products for individuals to
use, which is precisely where it is most unacceptable.  Therefore, we
have designed this version of the GPL to prohibit the practice for those
products.  If such problems arise substantially in other domains, we
stand ready to extend this provision to those domains in future versions
of the GPL, as needed to protect the freedom of users.

  Finally, every program is threatened constantly by software patents.
States should not allow patents to restrict development and use of
software on general-purpose computers, but in those that do, we wish to
avoid the special danger that patents applied to a free program could
make it effectively proprietary.  To prevent this, the GPL assures that
patents cannot be used to render the program non-free.

  The precise terms and conditions for copying, distribution and
modification follow.
"""
