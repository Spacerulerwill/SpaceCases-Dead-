"""
Copyright (C) 2023 William Redding - All Rights Reserved

Module containing cross language support functionality

Functions
~~~~~~~~~
* get_locale_fm
* get_locale

See end of file for licence details
"""


def get_locale_fm(lang: str, str, *args) -> str:
    """Get text in specific language from lang data using a key and format it

    Args:
        lang: ISO code of the language
        str: the key
        *args: additional arguments to format the string
    Returns:
        The text in the specific language
    """
    return language_data[lang][str] % (args)


def get_locale(lang: str, str):
    """Get anything in specific language from the lang data using a key

    Args:
        lang: ISO code of the language
        str: the key
    Returns:
        Whatever it finds lol, anything can
    """

    return language_data[lang][str]


# supported_languages = ["en", "fr", "es", "de", "it", "ru"]
supported_languages = ["en"]

supported_languages_str = """
    🏴󠁧󠁢󠁥󠁮󠁧󠁿 English - `en`
    🇫🇷 Français - `fr`
    🇩🇪 Deutsch - `de`
    🇪🇸 Español - `es`
    🇮🇹 Italiano - `it`
    🇷🇺 Русский - `ru`
"""

from src.lang.en import en_data
from src.lang.de import de_data
from src.lang.es import es_data
from src.lang.fr import fr_data
from src.lang.it import it_data
from src.lang.ru import ru_data

language_data = {
    "en": en_data,
    "de": de_data,
    "es": es_data,
    "fr": fr_data,
    "it": it_data,
    "ru": ru_data,
}
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
