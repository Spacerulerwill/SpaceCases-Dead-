import os
import json

language_data = {

}

# get correct string and format it with arguments
def get_locale(lang, str, *args):
    return language_data[lang][str].format(*args)

def init():
    # go through lang files and load their data into language_data
    for lang_file in os.scandir("res/lang"):
        with open(lang_file.path) as f:
            language_data[os.path.splitext(os.path.basename(f.name))[0]] = json.load(f)
    
    print("Loaded language data")