"""
Copyright (C) 2023 William Redding - All Rights Reserved

Script that generates alphabet emojis used in the worlde game

See end of file for licence details
"""

from PIL import Image, ImageDraw, ImageFont
from string import ascii_uppercase

green = (83, 141, 78)
yellow = (181, 159, 59)
gray = (58, 58, 60)

colors = {green: "green", yellow: "yellow", gray: "gray"}

font = ImageFont.truetype("res/font/CONSOLA.ttf", 128, encoding="utf-8")


def create_letter_emoji(letter: str, bg_color: str):
    image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))

    draw = ImageDraw.Draw(image)

    # Draw a rounded rectangle
    draw.rounded_rectangle((0, 0, 128, 128), 32, fill=bg_color)

    text_width, text_height = draw.textsize(letter, font)
    position = ((128 - text_width) / 2 - 1, (128 - text_height) / 2 - 5)
    draw.text(position, letter, "white", font=font)

    image.save(f"res/images/emoji/wordle_letters/{letter}_{colors[bg_color]}.png")


if __name__ == "__main__":
    for color in colors.keys():
        for letter in ascii_uppercase:
            create_letter_emoji(letter, color)

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
