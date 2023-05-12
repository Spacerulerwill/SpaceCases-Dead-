"""
Script used to generate emoji images for every letter of the alphabet with multiple background colors
It is used in the wordle game.
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