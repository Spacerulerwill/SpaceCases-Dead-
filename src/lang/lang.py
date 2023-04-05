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
