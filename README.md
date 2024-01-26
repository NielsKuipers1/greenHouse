# State of the ✨*art*✨

Motor 1 is meant to be left motor pointing "from you", motor 2 - right motor pointing to you.

I tested the code with one motor connecting it to both motor ports - it seems to be turning in the expected direction.

# possible issues when using it on the gantry:
- I don't know where the top or bottom of the camera is but I assume bottom is where the wire is.
- Camera is oriented properly gantry doesn't follow a ball but runs away instead.

  Possible reason: orientation image is not oriented the way I expected.

  Fix: lines 24-26 in *main.py* have variable *to_follow*. negate X or Y of that variable. 

  Possible reason: I made a mistake with orientation of motors (although I checked it a million times).

  Fix: changed direction (True's and False's) on lines 78,79 in *control.py*
- Too slow/fast movement: 

  line 29 in *main.py* scales movement down by multiplying by 0.003, you can try changing it. Lines 67-74 in *control.py* limit movement speed. You can try changing the limit.
- 'ripped' movement: 'destination' updates every time a frame is checked, I don't think that can be done any faster other than by making a separate thread for motors. I personally think it is not unnecessary.