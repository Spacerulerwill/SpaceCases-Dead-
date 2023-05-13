"""
Copyright (C) 2022 William Redding - All Rights Reserved

The home of all cross file constants (to avoid circular dependencies)

See end of file for licence details
"""

from src.util.emojis import *

PREFIX = "cs "
TWELVE_HOURS = 43200
ONE_DAY = 86400
ONE_WEEK = ONE_DAY * 7
KEY_PRICE = 250

DEFAULT_INVENTORY_SIZE = 15
INVENTORY_ELEMS_PER_PAGE = 10
LEADERBOARD_ELEMS_PER_PAGE = 10
MAX_TRADES_PER_PAGE = 10
MAX_THREADS = 30

ROOM_DELETION_TIME = 900

HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36 OPRGX/104.0.4480.100"
}

# rarity to color
rarity_color_dict = {
    "consumer": 11584473,
    "industrial": 6199513,
    "milspec": 4942335,
    "high": 4942335,
    "restricted": 8931327,
    "remarkable": 8931327,
    "classified": 13839590,
    "exotic": 13839590,
    "covert": 15420235,
    "extraordinary": 15420235,
    "contraband": 14986809,
}

rarity_emoji_dict = {
    "consumer": CONSUMER_GRADE_EMOJI,
    "industrial": INDUSTRIAL_GRADE_EMOJI,
    "milspec": MILSPEC_EMOJI,
    "high": MILSPEC_EMOJI,
    "restricted": RESTRICTED_EMOJI,
    "remarkable": RESTRICTED_EMOJI,
    "classified": CLASSIFIED_EMOJI,
    "exotic": CLASSIFIED_EMOJI,
    "covert": COVERT_EMOJI,
    "extraordinary": COVERT_EMOJI,
    "contraband": CONTRABAND_EMOJI,
}

case_rarity_odds = {
    "rare items": 0.9974,
    "covert": 0.9910,
    "classified": 0.9590,
    "restricted": 0.7992,
    "milspec": 0.0000,
}

conditions = [
    "Factory New",
    "Minimal Wear",
    "Field Tested",
    "Well Worn",
    "Battle Scarred",
]

trade_up_rarity_dict = {
    "consumer": "industrial",
    "industrial": "milspec",
    "milspec": "restricted",
    "restricted": "classified",
    "classified": "covert",
}

# index of each condition in above list mapped to the lower bound of their ranges
case_wear_ranges_lower = {4: 0.45, 3: 0.38, 2: 0.15, 1: 0.07, 0: 0.00}
# index of each condition in above list mapped to the upper bound of their ranges
case_wear_ranges_upper = {4: 1.0, 3: 0.45, 2: 0.38, 1: 0.15, 0: 0.07}

# higher lower game constants
COSTS_MORE = True
COSTS_LESS = False

HL_MIN_GUESS = 5
HL_MAX_GUESS = 10

HL_PRICE = 250
HL_REWARD = lambda difficulty: ((difficulty - HL_MIN_GUESS) * 250) + HL_PRICE + 750

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
