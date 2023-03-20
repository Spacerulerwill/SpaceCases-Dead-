# Contributing

WARNING! All new features that contain text must be implemented in at least ENGLISH. See [here](#cross-language-compatibility) on how to implement text so it can have cross language support.

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
