from camera import CameraReader
from cv2 import imwrite
import web_app
import threading
import schedule
import time
import control as ctr
import numpy as np

class Main():
    def __init__(self):
        self.cam = CameraReader()
    
    def take_picture(self, plant_id):
        frame = self.cam.read()
        imwrite(f"static/pic{plant_id}.jpg", frame)

    def test_control(self):
        while True:
            # list of distances of circles to the center found by the camera, sorted by radius
            circles = self.cam.detect_red_tomatoes(self.cam.read())
            if circles:
                # take the biggest circle
                to_follow = circles[len(circles)-1]
                to_follow[0] = to_follow[0] if abs(to_follow[0])>10 else 0
                to_follow[1] = to_follow[1] if abs(to_follow[1])>10 else 0
                print(f"go {to_follow}")
                # scale distance in pixels down to meters
                ctr.move_dest_val(to_follow*0.03)
                # print(to_follow)
            ctr.control()

    def test_upright(self):
        i = 0
        while i < 20:
            ctr.move_dest_val(np.array([1, 1]))
            ctr.control
            time.sleep(0.2)
        ctr.motors_off()

i = 1
def pic_testing(m):
    global i
    m.take_picture(i)
    print(f"New_picture {i}")
    i = ((i+1)%3) + 1

    

if __name__ == "__main__":
    m = Main()
    # start a thread with web app
    m.test_upright()
    # threading.Thread(target=web_app.run_app, daemon=True).start()
    # schedule.every(20).seconds.do(pic_testing, m)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

