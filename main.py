from camera import CameraReader
from cv2 import imwrite
import web_app
import threading
import schedule
import time
import control as ctr
import numpy as np
import gantry_simulation as gs

class Main():
    def __init__(self):
        self.cam = CameraReader()
    
    def take_picture(self, plant_id):
        frame = self.cam.read()
        imwrite(f"static/pic{plant_id}.jpg", frame)

    def test_control(self):
        G = gs.Gantry([[0,0], [0, ctr.HEIGHT], [ctr.WIDTH, ctr.HEIGHT], [ctr.WIDTH, 0]], [0, 0])
        while True:
            # list of distances of circles to the center found by the camera, sorted by radius
            circles = self.cam.detect_red_tomatoes(self.cam.read(), True)
            if circles:
                # take the biggest circle
                to_follow = circles[len(circles)-1]
                to_follow[0] = to_follow[0] if to_follow[0]>10 else 0
                to_follow[1] = to_follow[1] if to_follow[1]>10 else 0
                # scale distance in pixels down to meters
                ctr.move_dest_val(to_follow*0.001)
                # print(to_follow)
                ctr.control()
            G.update(ctr.pos)

i = 1
def pic_testing(m):
    global i
    m.take_picture(i)
    print(f"New_picture {i}")
    i = ((i+1)%3) + 1

    

if __name__ == "__main__":
    m = Main()
    # start a thread with web app
    m.test_control()
    # threading.Thread(target=web_app.run_app, daemon=True).start()
    # schedule.every(20).seconds.do(pic_testing, m)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

