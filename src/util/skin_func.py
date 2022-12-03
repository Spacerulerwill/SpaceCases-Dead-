from typing import Tuple
from src.util import database
from src.util.constants import case_wear_ranges_lower, conditions
import random

# given the items unformatted name, it will generate a the float value and condition and whether it is stattrak
def gen_item(unformatted_name:str) -> Tuple[str, float]:
    skin_data = database.skin_data[unformatted_name]

    # select skin float
    min_float = skin_data["min_float"]
    max_float = skin_data["max_float"]

    float_value = random.random()
    
    #determine condition
    if float_value > 0 and float_value <= 0.1471:
        float_value = random.uniform(0.00, 0.07)
    elif float_value > 0.1471 and float_value <=  0.3939:
        float_value = random.uniform(0.07, 0.15)
    elif float_value > 0.3939 and float_value <= 0.8257:
        float_value = random.uniform(0.15, 0.38)
    elif float_value > 0.8257 and float_value <=   0.9007:
        float_value = random.uniform(0.38, 0.45)
    elif float_value > 0.9007 and float_value <= 1.0:
        float_value = random.uniform(0.45, 1)

    #linear interpolate between max and min float
    final_float = float_value * (max_float - min_float) + min_float

    for wear, upper in case_wear_ranges_lower.items():
        if final_float > upper:
            condition = conditions[wear].lower() + " "
            break

    #is it stattrak?
    if random.random() < 0.1:
        stattrak = "stattrak "
    else:
        stattrak = ""
    unformatted_name = stattrak + condition + unformatted_name

    return unformatted_name, final_float