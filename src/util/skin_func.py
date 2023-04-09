from typing import Tuple
from src.util import database
from src.util.constants import case_wear_ranges_lower, conditions
import random


def gen_item(unformatted_name: str, container_type: str) -> Tuple[str, float]:
    """Randomly generate a float and condition for a skin given its name, and determine if it's statrak

    Args:
        unformatted_name: the unformatted name of the skin
    Returns:
        a tuple of the new skin name and its float value
    """
    skin_data = database.skin_data["no_wear_skins"][unformatted_name]

    # select skin float
    min_float = skin_data["min_float"]
    max_float = skin_data["max_float"]

    float_value = random.random()

    # determine condition
    if float_value > 0 and float_value <= 0.1471:
        float_value = random.uniform(0.00, 0.07)
    elif float_value > 0.1471 and float_value <= 0.3939:
        float_value = random.uniform(0.07, 0.15)
    elif float_value > 0.3939 and float_value <= 0.8257:
        float_value = random.uniform(0.15, 0.38)
    elif float_value > 0.8257 and float_value <= 0.9007:
        float_value = random.uniform(0.38, 0.45)
    elif float_value > 0.9007 and float_value <= 1.0:
        float_value = random.uniform(0.45, 1)

    # linear interpolate between max and min float
    final_float = float_value * (max_float - min_float) + min_float

    for wear, upper in case_wear_ranges_lower.items():
        if final_float > upper:
            condition = conditions[wear].lower() + " "
            break

    # modifier
    modifier = ""
    if skin_data["has_souvenir_variant"]:
        if container_type == "souvenir_package":
            modifier = "souvenir "
    elif skin_data["has_stattrak_variant"]:
        if container_type == "case":
            if random.random() < 0.1:
                modifier = "stattrak "

    unformatted_name = modifier + condition + unformatted_name

    return unformatted_name, final_float
