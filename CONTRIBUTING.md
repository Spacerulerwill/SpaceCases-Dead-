# Contributing

WARNING! All new features that contain text must be implemented in at least ENGLISH. See [here](#cross-language-compatibility) on how to implement text so it can have cross language support.

# Setup

To successfully create an environment to implement new features and test them, you will need to do the following

* As this project is written in python, you can install the latest version [here](https://www.python.org/downloads/)
* Install [MongoDB Community Server](https://www.mongodb.com/try/download/community) - all the options left to default!
* Go to the [discord developer portal](https://discord.com/developers/applications), login and click **New Application**
* Go click on bot tab on the left, and then click **Add Bot**
* Scroll down to the "Privileged Gateway Intents" section and tick all three
* Click the **Copy** button to copy its token and save it somewhere temporarily. Don't lose it!
* Create a fork of the repository and clone it to some folder.
* Go into that folder in the terminal and run the build.py file, pasting in your token when prompted
* Wait for it to finish
* Now you can go back to the discord developer portal and go to the OAuth2 tab, then to URL Generator and then check the "bot" box
* In the bot permissions box below check: 
    * Send Messages
    * Create Public Threads
    * Create Private Threads
    * Manage Messages
    * Manage Threads

Now you can invite your discord bot to a server with the url this has generated, run the bot and add some cool stuff!

# Implementation Guidelines
## Cross language compatibility
All phrases of text for the bot are stored in language specific JSON files with their own unqiue key identifier. For example:

* The text for the title of the balance embed is stored with the key `"balance.embed.title"`

Text that changes depending on variables must be stored as formatted strings. In the previous example, the value of `"balance.embed.title"` is `"{}'s balance"` in [`en.json`](res/lang/en.json) so the string can be formatted to insert the user's name

The files are located in [`res/lang/`](res/lang) and are named according to the [ISO Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).

## Amending existing translations or adding missing translations
To do this all you need to do is go to [`res/lang/`](res/lang) and find the correct file for your language, using the [ISO Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).
Then you can amend phrases as needed.

## Implementing a new language
To implement a new language:
* Find your [ISO Language Code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
* Go to [`src/util/lang.py`](src/util/lang.py) and add this code, all lowercase, to the `supported_languages` variable
* Go to [`res/lang/`](res/lang) and create a new json file, in format `{}.json` where `{}` is the ISO code
* It is recommended to copy the contents of [`en.json`](res/lang/en.json) into the new file as the english file will always be up to date with the text. Then you can change all the english to your language.
* If you do not implement all the phrases, do not leave empty strings like this:    
  ```json
  {
    "blah.blah.blah": ""
  }
  ```
  It is best to just leave that one entirely, the bot will catch the key error and provide a default string instead.