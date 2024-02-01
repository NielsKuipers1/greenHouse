"""
temporary file to simulate sensor output
"""
from random import uniform
def get_plant_info(plant_id: int): 
    return {"humidity": round(uniform(0.3, 0.8), 2)}