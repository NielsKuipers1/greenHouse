#import RPi.GPIO as GPIO
import numpy as np
#from RpiMotorLib import RpiMotorLib
import keyboard
import time

import gantry_simulation as gs

WHEEL_DIAM = 0.011
METERS_PER_ROTATION = WHEEL_DIAM*3.14

#GPIO layout
DIR_1 = 22
STEP_1 = 23
EN_PIN_1 = 24 # LOW to enable
# TODO: V
DIR_2 = 0
STEP_2 = 0
EN_PIN_2 = 0 # LOW to enable

# TODO: measure actual width and height
WIDTH = 0.375
HEIGHT = 0.39

pos = np.array([0.0, 0.0])
dest = np.array([0.0, 0.0])

#setup and enable motors
# motor_1 = RpiMotorLib.A4988Nema(DIR_1, STEP_1, (-1,-1,-1), "DRV8825")
# motor_2 = RpiMotorLib.A4988Nema(DIR_2, STEP_2, (-1,-1,-1), "DRV8825")

# GPIO.setup(EN_PIN_1, GPIO.OUT)
# GPIO.setup(EN_PIN_2, GPIO.OUT)
# GPIO.output(EN_PIN_1,GPIO.LOW)
# GPIO.output(EN_PIN_2,GPIO.LOW)

# def enable_motors(on: bool):
#     if on:
#         GPIO.output(EN_PIN_1,GPIO.LOW)
#         GPIO.output(EN_PIN_2,GPIO.LOW)
#     else:
#         GPIO.output(EN_PIN_1,GPIO.UP)
#         GPIO.output(EN_PIN_2,GPIO.UP)

def _convert_to_rotation(vec: np.ndarray) -> np.ndarray:
    """
    given change in XY coordinates returns rotations for motor 1 and 2
    """
    return [(vec[0]+vec[1])/METERS_PER_ROTATION, (vec[0]-vec[1])/METERS_PER_ROTATION]

def _move(vec: np.ndarray):
    """
    given move vector turns motor to move the EE
    if vector points outside of field of movement "shortens it"
    and makes it parallel to the edge
    """
    global pos
    end_point = vec+pos
    if (end_point[0]>WIDTH):
        vec[0] = WIDTH-pos[0]
    if (end_point[0]<0):
        vec[0] = -pos[0]
    if (end_point[1]>HEIGHT):
        vec[1] = HEIGHT-pos[1]
    if (end_point[1]<0):
        vec[1] = -pos[1]

    rot = _convert_to_rotation(vec)

    # try-except blocks needed because apparently convertion to int may fail at very low values
    try:
        steps_1 = int(200*rot[0])
    except ValueError:
        steps_1 = 0
    try:
        steps_2 = int(200*rot[1])
    except ValueError:
        steps_2 = 0 

    # motor_1.motor_go(True if rot[0]>0 else False, steptype="Full", steps=steps_1)
    # motor_2.motor_go(False if rot[1]>0 else True, steptype="Full", steps=steps_2)

def control():
    """
    moves EE towards the destination
    """
    global dest, pos
    vmax = np.vectorize(max)
    vmin = np.vectorize(min)
    vec = vmax(-0.005, vmin(0.005, dest-pos))
    _move(vec)
    pos += vec

def move_dest_val(vec):
    global dest, pos
    """
    change destination of the EE
    """
    dest = pos+vec

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
    # GPIO.cleanup()