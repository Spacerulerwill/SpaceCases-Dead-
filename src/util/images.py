"""
Copyright (C) 2023 William Redding - All Rights Reserved

The home of image url constants

See end of file for licence details
"""

import requests
from io import BytesIO
from PIL import Image

T_LOGO = "https://static.wikia.nocookie.net/cswikia/images/e/e0/Icon-t-patch-small.png/revision/latest?cb=20220130164538"
CT_LOGO = "https://static.wikia.nocookie.net/cswikia/images/b/ba/Ct-patch-small.png/revision/latest?cb=20220130164507"

CASE = "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIYQNqhpOSV-fRPasw8rsRVx4MwFo5_T3eAQ3i6DMIW0X7ojiwoHax6egMOKGxj4G68Nz3-jCp4itjFWx-ktqfSmtcwqVx6sT/256fx256f"
PACKAGE = "https://community.cloudflare.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIYQNqhpOSV-fRPasw8rsUlNhJw1EiamxJBVlw-HHfDIMuonkl4XbkaTyZOvXzzkAvZIk07jAp9Xx21Hn_RVuMDyhd9WXdVA4ZUaQpAaRvoU2Gw/360fx360f"
SOUVENIR_PACKAGE = "https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIYQNqhpOSV-fRPasw8rsUVhmKQ1Z5Or0cjhwwfzFfgJG6eO4gYuO2fOhMLjTkzsIu8Eh0-uVooin2ATjrhBqYmqnJYaRcVJrMw2Dr1K8yLzxxcjrNL980ec/256fx256f"
STICKER_CAPSULE = "https://community.akamai.steamstatic.com/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIYQNqhpOSV-fRPasw8rsQEl9Jg9SpIW1KgRr7PDbI219792mh5WHkrn1NeLTwTxSu8QmiLvEptumiwW1rRE-MGD1JI_AIAA7ZliCqAS9wOzsm9bi65vhLWPP/360fx360f"

EMPTY_CONTRACT_URL = "https://static.wikia.nocookie.net/cswikia/images/a/a3/Csgo_contrect.png/revision/latest?cb=20180507174532"
EMPTY_CONTRACT_IMAGE = Image.open(BytesIO(requests.get(EMPTY_CONTRACT_URL).content))

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
