from src.util.constants import PREFIX
from src.util.constants import KEY_PRICE
from src.lang.lang import supported_languages_str
from src.util.string_util import currency_str_format
from src.commands.games.higher_lower import HL_MAX_GUESS, HL_MIN_GUESS, HL_PRICE

KEY_PRICE_STR = currency_str_format(KEY_PRICE)
HL_PRICE_STR = currency_str_format(HL_PRICE)

en_data = {
    "welcome_message": f"Hello! My name is **%s**\n\nI am CS:GO case unboxing and economy bot. With me you can:\n• Unbox your dream skins\n• Trade them with other users\n• Take a risk and upgrade them\n• And more coming soon!\n\nBy default, users can open cases in any channel where they can type. This can cause a lot of clutter, so it is recommended you use `{PREFIX}config` to set up a room creation channel so users can unbox in their own threads\n\nEnjoy! - [Spacerulerwill](https://github.com/Spacerulerwill)\n\nUse `{PREFIX}info` to see this message again at anytime",
    # CS TERMS
    "consumer": "Consumer Grade",
    "industrial": "Industrial Grade",
    "milspec": "Mil-Spec",
    "restricted": "Restricted",
    "classified": "Classified",
    "covert": "Covert",
    "contraband": "Contraband",
    "rare items": "Rare Items",
    "Factory New": "Factory New",
    "Minimal Wear": "Minimal Wear",
    "Field Tested": "Field Tested",
    "Well Worn": "Well Worn",
    "Battle Scarred": "Battle Scarred",
    # TYPES
    "int": "an whole number",
    "Decimal": "a number",
    # GENERIC TEXT
    "rarity": "Rarity",
    "price_range": "Price Range",
    "float_range": "Float Range",
    "float": "Float",
    "market_value": "Market Value",
    "chance": "Chance",
    "price_multiplier": "Price Mulitplier",
    "commands": "Commands",
    "none": "None",
    "None": "None",
    "backtick_none": "`None`",
    "inspect_in_3d": "[Inspect In 3D](%s)",
    # BUTTONS
    "button.add_to_inventory": "Add To Inventory",
    "button.sell": "Sell",
    "button.cancel": "Cancel",
    "button.continue": "Continue",
    "button.upgrade": "Upgrade",
    "button.start": "Start",
    "button.less": "Less",
    "button.more": "More",
    "button.clear": "Clear",
    "button.edit": "Edit",
    "button.sign": "Sign",
    # GENERIC ERROR MESSAGES
    "command_not_found": "Command not found!",
    "command_not_found_suggest": "Command not found! Did you mean `%s`?",
    "command_error.no_user": "**Error!** Could not find user!",
    "command_error.incorrect_type": "**Error!** Argument `%s` must be %s",
    "command_error.missing_required_argument": "**Oops!** You forgot to supply the argument: `%s`",
    "command_error.invalid_option": "**Error!** Argument must be one of the following options: `%s`",
    "command_error.missing_permissions": "**Error!** You are missing the following permissions to use this command: `%s`",
    "command_error.cooldown": "**Command is on cooldown!** Try again after %.2fs seconds",
    "command_error.room": f"This command must be used in a room! Go to %s and use `{PREFIX}room`",
    "author_not_registered": f"You are not registered! Use `{PREFIX}register` to register",
    "user_not_registeed": "%s is not registered!",
    "not_your_button": "This is not your button!",
    "not_your_select": "This is not your select menu!",
    "invalid_page": "Invalid page number!",
    "not_enough_funds": "You don't have enough funds for this action!",
    # USER COG
    "lang.current": "Current Language: `English`",
    "lang.embed.supported_languages": "Supported Languages",
    "lang.not_found": "Langauge is not supported! Choose your language using the list below",
    "balance.embed.title": "%s's Balance",
    "balance.current": "Current Balance",
    "balance.return": "Total Return",
    "register.already_registered": "You are already registered!",
    "register.success": f"Registered! Use `{PREFIX}claim` to claim some money!",
    "transfer.cant_transfer_to_self": "You can't transfer money to yourself!",
    "transfer.amount_greater_than_0": "The amount must be greater than $0!",
    "transfer.insufficient_funds": "You have insufficient funds!",
    "transfer.successfull": "Successfully transferred %s to %s's account",
    "claim.embed.title": "You have successfully claimed your daily reward!",
    "claim.embed.description": "You can claim again tomorrow",
    "claim.embed.footer": "Warning: Streaks reset 24 hours after your last claim",
    "claim.embed.footer.bonus_item": "\nWarning: You have 3 minutes to claim your item!",
    "claim.already": "You have already claimed your daily reward! You can claim again tomorrow",
    "claim.embed.amount": "Amount",
    "claim.embed.new_balance": "New Balance",
    "claim.embed.streak": "Streak 🔥",
    "claim.embed.bonus_item": "You got a bonus item!",
    "room.cannot_create_here": "You cannot create rooms here!",
    "room.not_setup": f"This server does not have rooms set up yet. You can either unbox without a room, or ask an **admin** to use `{PREFIX}config` to set it up",
    "room.not_in_channel": "You must be in %s to create a room!",
    "room.exists": "%s already exists",
    "room.private_created": "Your private room has been created!",
    "room.greeting": "Welcome to your room %s! It will be deleted after 15 minutes of inactivity",
    # INVENTORY COG
    "inventory.embed.empty_title": "%s's Inventory",
    "inventory.embed.title": "%s's Inventory - %s/%s",
    "inventory.embed.description": "Total value: **%s**\nSlots Used: **%s/%s**",
    "inventory.item_string": "%s **%s)** `%s` - **%s**\n",
    "inventory.full": "Your inventory is full! Sell an item or buy more inventory space",
    "inventory.empty_1": f"Your inventory is empty! Start unboxing with `{PREFIX}open`",
    "inventory.empty_2": "%s's inventory is empty!",
    "inventory.not_found_index": "No item exists at index %s",
    "inventory.not_found_name": "No item exists with name `%s`",
    "inventory.embed.commands_1": f"""`{PREFIX}inspect <item number>` - view an item
    `{PREFIX}sell <item number>` - sell an item""",
    "inventory.embed.commands_2": f"`{PREFIX}inspect %s <item number>` - see an item",
    "sell.item_missing": "Sell cancelled as the specific **%s** is no longer in your inventory",
    "sell.are_you_sure": "Are you sure you want to sell **%s** for **%s**?",
    "sell.success": "Successfully sold **%s**",
    # UNBOX COG
    "container.not_found": "Container not found!",
    "container.not_found_suggest": "Container not found! Did you mean: `%s`?",
    "container.select.all_items": "All Items",
    "containers.embed.title": "Page %s/%s - %s",
    "containers.embed.description": f"Use `{PREFIX}container <container>` to see a container's contents and `{PREFIX}open <container>` to open one",
    "containers.embed.footer": f"Warning! Case prices do not include price of case key ({KEY_PRICE_STR})",
    "containers.select.label.all_containers": "All Containers",
    "containers.select.label.cases": "Cases",
    "containers.select.label.souvenir_packages": "Souvenir Packages",
    "containers.select.label.sticker_capsules": "Sticker Capsules",
    "item.not_found": "Could not find item!",
    "item.not_found_suggest": "Could not find item! Did you mean: `%s`?",
    "open.embed.footer": "Warning! Items are automatically sold after 30 seconds",
    "upgrade.cant_upgrade_to_cheaper_item": "Result item must be worth more than starting item!",
    "upgrade.embed.title": "**Upgrading**: %s\n**To**: %s",
    "upgrade.embed.footer": "Warning! Upgrades will cancel after 30 seconds",
    "upgrade.error.title": "Upgrade Error",
    "upgrade.error.item_missing": "Failed to upgrade as **%s** no longer exists in inventory",
    "tradeup.error.same_item_twice": "You cannot use the same item twice in a tradeup!",
    "tradeup.error.not_enough_items": "You must provide 10 items for contract",
    "tradeup.error.not_all_found": "Not all skins found in inventory!",
    "tradeup.error.not_same_rarity": "All items must be of the same rarity",
    "tradeup.error.stattrak_mix": "You cannot mix StatTrak and non StatTrak items!",
    "tradeup.error.invalid_items": "Not all items you have chosen can be traded up!",
    "tradeup.footer": "Contract signing will be cancelled after 30 seconds",
    # RANKINGS COG
    "leaderboard.embed.title": "Leaderboard - #%s - %s",
    "leaderboard.footer": "Leaderboard updates every hour",
    "ranking.text": "%s is at position **#%s** on the leaderboard",
    # GAMES COG
    "greater_than_0": "You must bet more than **$0**!",
    "cannot_be_negative": "You cannot bet negative!",
    "cannot_play_against_self": "You cannot play this game against yourself!",
    "coinflip.win.embed.title": "You Won **%s**!",
    "coinflip.loss.embed.title": "You Lost **%s**!",
    "coinflip.loss.embed.description": "Better luck next time",
    "hl.embed.title": "Higher or Lower",
    "hl.embed.description": f"Welcome to the **Higher or Lower** game!\n\nIn this game you must guess if the skin you see is more or less expensive than the previous one. Get all **%s** correct and you will win balance! The game costs **{HL_PRICE_STR}**.\n\nThe first skin is shown to you below. Press the **Start** button to begin.\n",
    "hl.embed.footer": "Warning! Menu will close after 30 seconds",
    "hl.invalid_difficulty": f"Difficulty must be in range {HL_MIN_GUESS} to {HL_MAX_GUESS}",
    "hl.playing.embed.title": "Higher or Lower - %s/%s",
    "hl.playing.embed.description": "Does this skin cost more or less than the previous?\nDecide within **10 seconds**\n\n",
    "hl.playing.won.embed.title": "Congratulations!",
    "hl.playing.won.embed.description": "You won **%s**",
    "hl.playing.lost.embed.title": "You Lost!",
    "hl.playing.lost.embed.out_of_time": "You ran out of time!",
    "hl.playing.lost.embed.incorrect_guess": "Previous Item: **%s - %s**\nYour Choice: **%s - %s**",
    "skin_game.embed.title": "Guess the skin!",
    "skin_game.embed.description": "Reply with the name of the skin within 10 seconds!\nDo **not** include the wear or the weapon name!",
    "skin_game.won": "You guessed **correctly!** You win **%s**",
    "skin_game.lost.incorrect_guess": "You guessed **incorrectly!** The correct answer was `%s`",
    "skin_game.lost.out_of_time": "You did not reply in time! The correct answer was `%s`",
    "ttt.embed.title": "Tic Tac Toe",
    "ttt.embed.description": "**%s** vs **%s**\nEach player will have 10 seconds to make their move.\n**%s** must click the button below to accept!",
    "ttt.embed.description_wager": "\nThe fee for playing this game is **%s**. Winner takes all!",
    "ttt.embed.footer": "Warning! Menu will close after 3 minutes!",
    "ttt.both_players_not_enough_funds": "Both players must have **%s** to play",
    "ttt.player_won": "%s won!",
    "ttt.draw": "Draw!",
    "ttt.player_turn": "%s's turn",
    "wordle.word_wrong_length": "Guess must be a 5 letter word!",
    "wordle.word_not_found": "Word must be a valid english word!",
    "wordle.won.embed.title": "You Won **%s**!",
    "wordle.loss.embed.title": "You Lost!",
    "wordle.loss.embed.description": "The word was `%s`\n",
    # TRADING COG
    "no_incoming_trade": "You do not have an incoming trade from %s",
    "no_outgoing_trade": "You have no outgoing trade with %s",
    "no_trade_in_creation": f"You have no trade in creation! Use `{PREFIX}trade new <user>` to start a new trade",
    "trade_error": "Trade Error",
    "trade_error.author_not_enough_space": "Your trade to %s could not take place as you don't have enough inventory space to recieve the items from the trade!",
    "trade_error.sender_not_enough_space": "Your trade to %s could not take place %s does not have enough inventory space to recieve the items from the trade!",
    "trade_error.missing_items": "The trade from %s could not take place and has been cancelled as items were missing from one or both participants inventories",
    "trade_error.already_have_trade_with_user": "You already have an outgoing trade to %s! You cannot have mutliple trades to one user",
    "you_are_missing": "You Are Missing",
    "sender_is_missing": "%s is Missing",
    "trade_accept.author_embed.description": "Trade request from %s accepted!",
    "trade_accept.sender_embed.title": "%s accepted your trade request!",
    "your_new_items": "Your new items",
    "trade_add.cannot_add_item_twice": "You cannot add the same item twice to a trade!",
    "trade_cancel.cancelled_trade_to_user": "Successfully cancelled trade to %s",
    "trade_cancel.cancelled_current": "Successfully cancelled trade in creation",
    "trade_decline.author_embed.description": "Trade request from %s declined",
    "trade_decline.sender_embed.title": "Your trade request to %s was declined",
    "your_items": "Your Items",
    "their_items": "Their Items",
    "you_wanted": "You Wanted",
    "for_your": "For Your",
    "they_offer": "They Offer",
    "trade_new.warning.embed.title": "Warning: You already have a trade request in creation",
    "trade_new.warning.embed.description": "This trade request will be deleted. Continue?",
    "trade_new.warning.embed.footer": "Trade request creation will automatically cancel after 30 seconds of inactivity",
    "trades.in.embed.title": "Incoming Trade Requests",
    "trades.out.embed.title": "Outgoing Trade Requests",
    "trades.all.embed.title": "All Trade Requests",
    "trades.incoming_from": "**INCOMING** from %s: **%s** days left\n",
    "trades.outgoing_to": "**OUTGOING** to %s: **%s** days left\n",
    "trades.embed.trade_list": "Trade List - %s Items - Page %s/%s",
    "trades.embed.commands.value": f"""`{PREFIX}trade in <user>` - view incoming trade from user'
    `{PREFIX}trade out <user>` - view outgoing trade to user
    `{PREFIX}trade accept <user>` - accept trade from user
    `{PREFIX}trade decline <user>` - decline trade from user
    `{PREFIX}trade cancel <user>` - cancel trade to user""",
    "trade_notif.embed.title": "%s has sent you a trade request!",
    "trade_notif.commands.value": f"""`{PREFIX}trade accept %s` - accept trade
    `{PREFIX}trade decline %s` - decline trade""",
    "trade_embed.incoming_title": "Incoming trade from %s",
    "trade_embed.outgoing_title": "Outgoing trade from %s",
    "trade_embed.footer": "Trade expires in %s days, %s hours and %s minutes",
    "trade_embed.commands.value": f"`{PREFIX}trade cancel %s` - cancel trade",
    "trade_in_creation_embed.unsent.title": "Trade request to %s",
    "trade_in_creation_embed.sent.title": "Sent trade request to %s",
    "trade_in_creation_embed.sent.footer": "Warning! Trade will expire in 1 week",
    "trade_in_creation_embed.unsent.commands.value": f"""`{PREFIX}trade cancel` - cancel trade
    `{PREFIX}trade add in/out <inventory item number>` - add item
    `{PREFIX}trade remove in/out <trade item number>` - remove item
    `{PREFIX}trade send` - send trade""",
    # HELP COG
    "help.embed.description": f"Use `{PREFIX}help <command>` to gain more information about that command'",
    "help.aliases": "Aliases",
    # CONFIG COG
    "config.options.room_channel.name": "Unboxing Room Creation Channel",
    "config.options.room_channel.description": "Channel used to create rooms to unbox cases in. If set to `None` users can unbox anywhere I can message in the server",
    "config.options.room_channel.response_embed_text": "Respond to this message with name of text channel within **30 seconds**",
    "config.menu.footer ": "Warning! Menu will close itself after 3 minutes of inactivity",
    "config.menu.description": "%s\n\n**Current Value**: %s",
    "config.current_value": "**Current Value**: %s",
    "config.no_response": "Editing **%s** cancelled due to no response",
    "config.set_default_value": "Set **%s** to default value: `%s`",
    "config.successful_change": "Successfully set **%s** to %s",
    "config.conversion_fail": "Conversion Failure",
    # COMMAND INFORMATION
    "register.description": "Register a bank account",
    "register.usage": {"Syntax": f"`{PREFIX}register`"},
    "lang.description": "View or change your current language",
    "lang.usage": {
        "Syntax": f"`{PREFIX}lang <language>`",
        "Arguments": "**OPTIONAL** `language`: ISO code of language to switch to",
        "Supported Languages": supported_languages_str,
    },
    "balance.description": "Check a user's balance",
    "balance.usage": {
        "Syntax": f"`{PREFIX}balance <user>`",
        "Arguments": "**OPTIONAL** `user`: User to check balance of",
    },
    "claim.description": "Claim your daily reward",
    "claim.usage": {"Syntax": f"`{PREFIX}claim`"},
    "room.description": "Create a room for unboxing items in",
    "room.usage": {
        "Syntax": f"`{PREFIX}claim <type>`",
        "Arguments": """**OPTIONAL** `type`: which type of room to open:
        • public - **DEFAULT**
        • private
        """,
        "Additional Information": f"This command can only be used if rooms are enabled in your guild. Get an admin to turn on rooms with `{PREFIX}config` to use them. If they are enabled you can only used this room in a designated room creation channel",
    },
    "transfer.description": "Transfer money to another user",
    "transfer.usage": {
        "Syntax": f"`{PREFIX}transfer <user> <amount>`",
        "Arguments": """`user`: the recipient of the money
        `amount`: the amount of money to transfer
        """,
    },
    "open.description": "Buy and open a container",
    "open.usage": {
        "Syntax": f"`{PREFIX}open <container>`",
        "Arguments": "`container`: the container to open",
        "Additional Information": f"Use `{PREFIX}containers` to view a list of containers available for purchase",
    },
    "item.description": "View the details of a specific item",
    "item.usage": {
        "Syntax": f"`{PREFIX}item <item>`",
        "Arguments": "`item`: the name of the item",
        "Additional Information": """
        All item names are formmatted without any punctuation
        Weapons: `modifier` `condiion` `weapon name` `skin name`
        Examples:
        • `stattrak factory new awp dragon lore`
        • `souvenir well worn ak 47 gold arabesque`
        • `field tested usp s cortex`
        """,
    },
    "containers.description": "View all containers available for purchase",
    "containers.usage": {"Syntax": f"`{PREFIX}containers`"},
    "container.description": "View a container's contents",
    "container.usage": {
        "Syntax": f"`{PREFIX}`container <container>",
        "Arguments": "`container`: name of container to inspect",
        "Additional Information": f"Use `{PREFIX}containers` to view a list of containers available for purchase",
    },
    "upgrade.description": "Take a chance to upgrade an item to one of higher value",
    "upgrade.usage": {
        "Syntax": f"`{PREFIX}upgrade <item index> <desired item name>`",
        "Arguments": """`item index`: the inventory index of the item to upgrade
        `desired item name`: the name of the item you want to upgrade too""",
        "Additional Information": """
        All item names are formmatted without any punctuation
        Weapons: `modifier` `condiion` `weapon name` `skin name`
        Examples:
        • `stattrak factory new awp dragon lore`
        • `souvenir well worn ak 47 gold arabesque`
        • `field tested usp s cortex`
        """,
    },
    "leaderboard.description": "View the global leaderboard",
    "leaderboard.usage": {
        "Syntax": f"`{PREFIX}leaderboard <page>`",
        "Arguments": "**OPTIONAL** `page`: page of the leaderboard",
    },
    "ranking.description": "View a user's ranking on the global leaderboard",
    "ranking.usage": {
        "Syntax": f"`{PREFIX}ranking <user>`",
        "Arguments": "**OPTIONAL** `user`: user to check ranking of",
    },
    "inventory.description": "View a user's inventory",
    "inventory.usage": {
        "Syntax": f"`{PREFIX}inventory <user> <page>`",
        "Arguments": """**OPTIONAL** `user`: user whos inventory to view
        **OPTIONAL** `page`: page of inventory to view
        """,
    },
    "inspect.description": "Inspect an item in a user's inventory",
    "inspect.usage": {
        "Syntax": f"`{PREFIX}inspect <item index> <user>`",
        "Arguments": """`item index`: index of item to inspect
        **OPTIONAL** `user`: which users inventory the item is in
        """,
    },
    "sell.description": "Sell an item from your inventory",
    "sell.usage": {
        "Syntax": f"`{PREFIX}sell <item index>`",
        "Arguments": "`item index` the index of the item you wish to sell",
    },
    "coinflip.description": "Flip a coin to double your bet or lose it all",
    "coinflip.usage": {
        "Syntax": f"`{PREFIX}coinflip <side> <bet>`",
        "Arguments": """`side`: which side the coin will land on. Can be:
        • t
        • ct
        `bet`: how much money to risk on the coinflip
        """,
    },
    "hl.description": "Play the higher lower skin guessing game!",
    "hl.usage": {
        "Syntax": f"{PREFIX}hl <difficulty>",
        "Arguments": f"**OPTIONAL `difficulty`: how many correct guesses needed to win ({HL_MIN_GUESS}-{HL_MAX_GUESS})",
        "How To Play": """In this game you are shown a skin to start with, then the game starts. You have to guess whether the next skin is more or less expensive just from the picture. Get them all right and you win money!""",
    },
    "skin_game.description": "Guess the name of the skin from the image",
    "skin_game.usage": {"Syntax": f"`{PREFIX}skin?`"},
    "ttt.description": "Play Tic Tac Toe against another user",
    "ttt.usage": {
        "Syntax": f"`{PREFIX}ttt <player2> <bet>`",
        "Arguments": """`player2`: opponent
        **OPTIONAL** `bet`: amount of money to bet on the game""",
    },
    "wordle.description": "Play WORDLE to win money!",
    "wordle.usage": {
        "Syntax": f"`{PREFIX}wordle <guess>`",
        "Arguments": "`guess` - your 5 letter guess",
        "How To Play": """Try and guess the 5 letter word in 6 guesses! When you guess a word, a letter will show:
        • **Green** if it is the correct letter in the correct place
        • **Yellow** if the letter is in the word but is in the wrong place
        • **Gray** if the letter is not in the word at all
        """,
    },
    "trade_accept.description": "Accept a trade from a user",
    "trade_accept.usage": {
        "Syntax": f"`{PREFIX}trade accept <sender>`",
        "Arguments": "`sender`: the sender of the trade",
    },
    "trade_add.description": "Add an item to your trade in creation",
    "trade_add.usage": {
        "Syntax": f"`{PREFIX}trade add <in/out> <item index>`",
        "Arguments": """
        `in/out`: whether to add the item to incoming or outgoing items. Either:
        • in
        • out
        `item index`: item index of item to add
        """,
    },
    "trade_remove.description": "Remove an item to your trade in creation",
    "trade_remove.usage": {
        "Syntax": f"`{PREFIX}trade remove <in/out> <item index>`",
        "Arguments": """
        `in/out`: whether to remove the item from incoming or outgoing items. Either:
        • in
        • out
        `item index`: item index of item to remove
        """,
    },
    "trade_cancel.description": "Cancel your trade in creation or a trade sent to another user",
    "trade_cancel.usage": {
        "Syntax": f"`{PREFIX}trade cancel <recipient>`",
        "Arguments": "**OPTIONAL** `recipient`: the recipient of the trade",
        "Additional Information": "If no recipient is provided, it will cancel your current trade in creation",
    },
    "trade_decline.description": "Decline an incoming trade from a user",
    "trade_decline.usage": {
        "Syntax": f"`{PREFIX}trade decline <sender>`",
        "Arguments": "`sender`: the sender of the trade",
    },
    "trade_in.description": "View an incoming trade from a user",
    "trade_in.usage": {
        "Syntax": f"`{PREFIX}trade in <sender>`",
        "Arguments": "`sender`: the sender of the trade",
    },
    "trade_new.description": "Create a new trade to a user",
    "trade_new.usage": {
        "Syntax": f"`{PREFIX}trade new <recipient>`",
        "Arguments": "`recipient`: the user you want to trade with",
    },
    "trade_out.description": "View an outgoing trade to a user",
    "trade_out.usage": {
        "Syntax": f"`{PREFIX}trade out <recipient>`",
        "Arguments": "`recipient`: the recipient of the trade",
    },
    "trade_send.description": "Finalise your trade and send it to a user",
    "trade_send.usage": {"Syntax": f"`{PREFIX}trade send`"},
    "info.description": "View the bot info message",
    "info.usage": {"Syntax": f"`{PREFIX}info`"},
    "config.description": "View the bot config menu",
    "config.usage": {"Syntax": f"`{PREFIX}config`"},
    "tradeup.description": "Trade up 10 skins of one quality to get one skin of the next quality up!",
    "tradeup.usage": {
        "Syntax": f"`{PREFIX}tradeup <item indexes>`",
        "Arguments": "`item indexes`: 10 inventory item indexes seperated by spaces",
        "Additional Information": """
        For a trade up, the items being traded up must meet these conditions:
        • **All** must be same rarity
        • **All** must be either StatTrak or not StatTrak, no mixing!
        • **All** must be guns - no gloves, knives or souvenirs!
        • **All** must be not the highest rarity in their respective collection/case
        """ 
    }
}
