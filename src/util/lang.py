import os
import json

language_data = {}

supported_languages = ["en", "fr", "es", "de", "it", "ru"]


def get_locale(lang: str, str, *args):
    """Get text in specific language form json data using a key

    Args:
        lang: ISO code of the language
        str: the key
        *args: additional arguments to format the string
    Returns:
        The text in the specific language
    """
    return language_data[lang][str].format(*args)


def init():
    # go through lang files and load their data into language_data
    for lang_file in os.scandir("res/lang"):
        with open(lang_file.path, encoding="utf-8") as f:
            language_data[os.path.splitext(os.path.basename(f.name))[0]] = json.load(f)
        print(f"Loaded language: {lang_file.name}")
