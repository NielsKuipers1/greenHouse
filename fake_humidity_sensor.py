"""
temporary file to simulate sensor output
"""
from random import random
def get_plant_info(plant_id: int): 
    return {"humidity": random(0.3, 0.8), "temperature": 21.3, "light": 123}