from camera import CameraReader
from cv2 import imwrite
from enum import Enum

import web_app
import threading
import schedule
import time
import control
import numpy as np
import gantry_simulation as gs

# coordinates of plants (made up, of course)
PLANTS = [np.array([0.1, 0.13]), 
          np.array([0.275, 0.13]), 
          np.array([0.187, 0.26])]


class GantryState(Enum):
    IDLE = 0
    TRACKING_TOMATO = 1
    MOVING_TO_PLANT = 2
    RETURNING_TO_START = 3


class Main():
    def __init__(self):
        self.G = gs.Gantry([[0,0], [0, control.HEIGHT], [control.WIDTH, control.HEIGHT], [control.WIDTH, 0]], [0, 0])
        self.ctr = control.Controller()
        self.cam = CameraReader()
        self.current_plant = 0
        self.event = threading.Event()
        self.state = GantryState.IDLE
        self.stop = False
        self.state_handler = {
            GantryState.IDLE: self.handle_idle,
            GantryState.MOVING_TO_PLANT: self.handle_moving_to_plant,
            GantryState.TRACKING_TOMATO: self.handle_tracking_tomato,
            GantryState.RETURNING_TO_START: self.handle_returning_to_start
        }


    def handle_idle(self):
        self.event.wait()
        if self.stop: 
            print("DEAD")
            return

        self.event.clear()
        self.current_plant = 0
        self.state = GantryState.MOVING_TO_PLANT

    def handle_moving_to_plant(self):
        self.ctr.set_dest(PLANTS[self.current_plant])
        self.ctr.control()

        if len(self.cam.detect_red_tomatoes(self.cam.read(), show=True)) > 0 and self.ctr.close_to(PLANTS[self.current_plant]
                                                                                        ) or np.array_equal(self.ctr.pos, self.ctr.dest):
            self.state = GantryState.TRACKING_TOMATO

    def handle_tracking_tomato(self):
        """
        move to the found tomato for 50 iterations
        # if tomato not found in 50 iterations - skip
        """
        for _ in range(0, 50):
            centered = self.track_tomato()
            if centered: break
        
        self.take_picture(self.current_plant+1)
        if centered:
            print("Uno tomato")
            pass
        else:
            print("No tomato")
            pass

        # increment plant counter
        # if counter is at 0 - return to "base"
        self.current_plant = (self.current_plant+1)%3
        if self.current_plant == 0:
            self.state = GantryState.RETURNING_TO_START
        else:
            self.state = GantryState.MOVING_TO_PLANT

    def handle_returning_to_start(self):
        self.ctr.set_dest(np.array([0.0,0.0]))
        self.ctr.control()
        if  np.array_equal(self.ctr.pos, self.ctr.dest):
            self.state = GantryState.IDLE

    def take_picture(self, plant_id):
        frame = self.cam.read()
        imwrite(f"static/pic{plant_id}.jpg", frame)

    def tringger_event(self):
        self.event.set()

    def track_tomato(self) -> bool:
        """
        tracks a tomato, returns true if tomato is close to center of the frame, false otherwise
        """
        # list of distances of circles to the center found by the camera, sorted by radius
        circles = self.cam.detect_red_tomatoes(self.cam.read(), show=True)
        if circles:
            # take the biggest circle
            to_follow = circles[len(circles)-1]
            # if circle is close to cente rof the frame - return
            if to_follow[0]<10 and to_follow[1]<10:
                return True
            # scale distance in pixels down
            self.ctr.move_dest_val(to_follow*0.001)
            # print(to_follow)
            self.ctr.control()
            # regardless of whether or not position was updated in this iteration continue moving in previously set diraction 
        return False

    def run(self):
        while True:
            self.state_handler[self.state]()
            self.G.update(self.ctr.pos)
            if self.state == GantryState.IDLE and self.stop: break

    def test_trigger_check(self):
        time.sleep(3)
        self.tringger_event()
        time.sleep(2)
        self.stop = True
        self.tringger_event()


if __name__ == "__main__":
    m = Main()

    threading.Thread(target=m.test_trigger_check, daemon=True).start()
    m.run()
    
    # start a thread with web app
    # threading.Thread(target=web_app.run_app, daemon=True).start()
    # schedule.every(20).seconds.do(pic_testing, m)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    