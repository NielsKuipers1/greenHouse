SHOW_CAMERA = True
SHOW_GRAPH =  True

from camera import CameraReader
from cv2 import imwrite
from enum import Enum
from web_app import WebApp

import time
import threading
import control
import numpy as np
if SHOW_GRAPH: import gantry_simulation as gs


# coordinates of plants (made up, of course)
PLANTS = [np.array([control.WIDTH/3, control.HEIGHT/3]), 
          np.array([control.WIDTH/1.5, control.HEIGHT/3]), 
          np.array([control.WIDTH/2, control.HEIGHT/1.5])]


class GantryState(Enum):
    IDLE = 0
    TRACKING_TOMATO = 1
    MOVING_TO_PLANT = 2
    RETURNING_TO_START = 3


class Main():
    def __init__(self):
        if SHOW_GRAPH: self.G = gs.Gantry([[0,0], [0, control.HEIGHT], [control.WIDTH, control.HEIGHT], [control.WIDTH, 0]], [0, 0])
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
        tomatoes, _ = self.cam.detect_ripe_tomatoes(self.cam.read(), show=SHOW_CAMERA)
        if len(tomatoes) > 0 and self.ctr.close_to(PLANTS[self.current_plant]
                                                                                        ) or np.array_equal(self.ctr.pos, self.ctr.dest):
            self.state = GantryState.TRACKING_TOMATO

    def handle_tracking_tomato(self):
        """
        move to the found tomato for 50 iterations
        # if tomato not found in 50 iterations - skip
        """
        for _ in range(0, 150):
            centered, frame = self.track_tomato()
            if SHOW_GRAPH: self.G.update(self.ctr.pos)
            if centered: break
        
        self.save_frame(frame, self.current_plant+1)
        if centered:
            print("Uno tomato")
            pass
        else:
            print("No tomato")
            pass

        # increment plant counter
        # if counter is at 0 - return to "base"
        self.current_plant = (self.current_plant+1)%3
        time.sleep(0.8)
        if self.current_plant == 0:
            self.state = GantryState.RETURNING_TO_START
        else:
            self.state = GantryState.MOVING_TO_PLANT

    def handle_returning_to_start(self):
        self.ctr.set_dest(np.array([0.0,0.0]))
        self.ctr.control()
        if  np.array_equal(self.ctr.pos, self.ctr.dest):
            self.event.clear()
            self.state = GantryState.IDLE

    def take_picture(self, plant_id):
        frame = self.cam.read()
        imwrite(f"static/pic{plant_id}.jpg", frame)
    
    def save_frame(self, frame, plant_id):
        imwrite(f"static/pic{plant_id}.jpg", frame)

    def tringger_camera(self):
        self.event.set()

    def exit(self):
        self.stop = True
        self.event.set()

    def track_tomato(self) -> bool:
        """
        tracks a tomato, returns true if tomato is close to center of the frame, false otherwise
        """
        # list of distances of circles to the center found by the camera, sorted by radius
        circles, frame = self.cam.detect_ripe_tomatoes(self.cam.read(), show=SHOW_CAMERA)
        if circles:
            # take the biggest circle
            to_follow = np.array(circles[len(circles)-1])
            # if circle is close to cente rof the frame - return
            if abs(to_follow[0])<70 and abs(to_follow[1])<70:
                return True, frame
            # scale distance in pixels down
            self.ctr.move_dest_val(to_follow*0.0001)
            # print(to_follow)
            self.ctr.control()
            # regardless of whether or not position was updated in this iteration continue moving in previously set diraction 
        return False, frame

    def run(self):
        while True:
            self.state_handler[self.state]()
            if SHOW_GRAPH: self.G.update(self.ctr.pos)
            if self.state == GantryState.IDLE and self.stop: break


if __name__ == "__main__":
    m = Main()
    web_app = WebApp(m)
    # start a thread with web app
    
    # this won't let you quit using Ctrl+C but shows camera output
    threading.Thread(target=web_app.run, daemon=True).start()
    m.run()

    # this won't show camera output because it should be on main thread
    # threading.Thread(target=m.run, daemon=True).start()
    # web_app.run()