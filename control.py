DO_MOTORS = False


import numpy as np
import keyboard
import time

import gantry_simulation as gs


WHEEL_DIAM = 0.011
METERS_PER_ROTATION = WHEEL_DIAM*3.14

WIDTH = 0.375
HEIGHT = 0.39

if DO_MOTORS:
    import RPi.GPIO as GPIO
    from RpiMotorLib import RpiMotorLib
    #GPIO layout
    DIR_1 = 22
    STEP_1 = 23
    EN_PIN_1 = 24 # LOW to enable

    DIR_2 = 25
    STEP_2 = 8
    EN_PIN_2 = 7 # LOW to enable

class Controller:
    def __init__(self):
        self.pos = np.array([0.0, 0.0])
        self.dest = np.array([0.0, 0.0])
        # initialize pinout for motors
        if DO_MOTORS:
            self.motor_1 = RpiMotorLib.A4988Nema(DIR_1, STEP_1, (21,21,21), "DRV8825")
            self.motor_2 = RpiMotorLib.A4988Nema(DIR_2, STEP_2, (21,21,21), "DRV8825")

    def enable_motors(self, on: bool):
        if on:
            GPIO.output(EN_PIN_1,GPIO.LOW)
            GPIO.output(EN_PIN_2,GPIO.LOW)
        else:
            GPIO.output(EN_PIN_1,GPIO.UP)
            GPIO.output(EN_PIN_2,GPIO.UP)

    def close_to(self, ref: np.ndarray) -> bool:
        """
        returns true if current position is close to ref
        """
        return np.linalg.norm(self.pos - ref) < 0.05

    def control(self):
        """
        moves EE towards the destination
        """
        vmax = np.vectorize(max)
        vmin = np.vectorize(min)
        vec = vmax(-0.005, vmin(0.005, self.dest-self.pos))
        self._move(vec)
        self.pos += vec

    def move_dest_val(self, vec):
        """
        change destination of the EE by vec
        """
        self.dest = self.pos+vec

    def set_dest(self, new_dest):
        self.dest = new_dest

    def _move(self, vec: np.ndarray):
        """
        given move vector turns motor to move the EE
        if vector points outside of field of movement "shortens it"
        and makes it parallel to the edge
        """
        end_point = vec+self.pos
        if (end_point[0]>WIDTH):
            vec[0] = WIDTH-self.pos[0]
        if (end_point[0]<0):
            vec[0] = -self.pos[0]
        if (end_point[1]>HEIGHT):
            vec[1] = HEIGHT-self.pos[1]
        if (end_point[1]<0):
            vec[1] = -self.pos[1]

        rot = convert_to_rotation(vec)

        # try-except blocks needed because apparently conversion to int may fail at very low values
        try:
            steps_1 = int(200*rot[0])
        except ValueError:
            steps_1 = 0
        try:
            steps_2 = int(200*rot[1])
        except ValueError:
            steps_2 = 0 

        # here I would turn the motors but they don't work :(
        if DO_MOTORS:
            self.motor_1.motor_go(False if rot[0]>0 else True, steptype="Full", steps=steps_1)
            self.motor_2.motor_go(True if rot[1]>0 else False, steptype="Full", steps=steps_2)
            # wait for motors to turn
        time.sleep(0.01)

def convert_to_rotation(vec: np.ndarray) -> np.ndarray:
    """
    given change in XY coordinates returns rotations for motor 1 and 2
    """
    return [(vec[0]+vec[1])/METERS_PER_ROTATION, (vec[0]-vec[1])/METERS_PER_ROTATION]

def test_with_keyboard():
    global dest, pos
    # loop for testing using keyboard input

    G = gs.Gantry([[0,0], [0, HEIGHT], [WIDTH, HEIGHT], [WIDTH, 0]], pos)

    while True:
        print("loop")
        if keyboard.is_pressed('w'):
            dest[1] += 0.01
            print("W")
        elif keyboard.is_pressed('s'):
            dest[1] -= 0.01
            print("S")
        elif keyboard.is_pressed('a'):
            dest[0] -= 0.01
            print("D")
        elif keyboard.is_pressed('d'):
            dest[0] += 0.01
            print("D")
        elif keyboard.is_pressed('q'):
            break
        control()
        G.update(pos)
        time.sleep(0.1)