import cv2 
import json
"""
temporary file to simulate sensor output
"""
cam = cv2.VideoCapture(0)

def take_snapshot(plant_id: int):
    ret, frame = cam.read()
    if ret:
        cv2.imwrite(f"images/pic{plant_id}.jpg", frame)
    else:
        print("Error")
    
def get_plant_info(plant_id: int): 
    return {"humidity": 0.5, "temperature": 20, "light": 123}