import cv2
import threading
import queue
import numpy as np

class CameraReader(threading.Thread):
    def __init__(self, src=0):
        super(CameraReader, self).__init__()
        self.cap = cv2.VideoCapture(src)
        self.queue = queue.Queue()
        self.daemon = True
        self.start()

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("ERROR: couldn't read a frame\n")
                break
            if not self.queue.empty():
                try:
                    self.queue.get_nowait()   # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.queue.put(frame)

    def read(self):
        # return last frame, if empty - blocks until frame is available
        return self.queue.get()
    
    def detect_red_tomatoes(self, frame, show=False) -> [np.ndarray]:
        """
        detects red circles in the frame and returns a list of distances from the center
        """
        (h, w) = frame.shape[:2] # height and width of the image
        frame_center = np.array([w/2, h/2])
        circles = _detect_red_circles(frame)
        _remove_false_circles(circles)
        if show:
            if circles != []:
                for circle in circles:
                    circled = cv2.circle(frame, [int(circle[0]), int(circle[1])], int(circle[2]), (0,255,0),thickness=2)
                cv2.imshow("original", circled)
            else:
                cv2.imshow("original", frame)
        return [np.array([c[0],h-c[1]]-frame_center) for c in circles]

def _detect_red_circles(frame):
    """
    returns a list of circles [x, y, radius] of tomatoes
    """

    blur = cv2.GaussianBlur(frame, (13,13), 0)
    hsv_conv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # because hue wraps up and to extract as many "red objects" as possible, I define lower and upper boundaries for brighter and for darker red shades
    bright_red_lower_bounds = (0, 100, 100)
    bright_red_upper_bounds = (10, 255, 255)
    bright_red_mask = cv2.inRange(hsv_conv_img, bright_red_lower_bounds, bright_red_upper_bounds)

    dark_red_lower_bounds = (160, 100, 100)
    dark_red_upper_bounds = (179, 255, 255)
    dark_red_mask = cv2.inRange(hsv_conv_img, dark_red_lower_bounds, dark_red_upper_bounds)

    # after masking the red shades out, I add the two images 
    weighted_mask = cv2.addWeighted(bright_red_mask, 1.0, dark_red_mask, 1.0, 0.0)

    # then the result is blurred
    blurred_mask = cv2.GaussianBlur(weighted_mask,(9,9),3,3)

    # some morphological operations (closing) to remove small blobs 
    erode_element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilate_element = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    eroded_mask = cv2.erode(blurred_mask,erode_element)
    dilated_mask = cv2.dilate(eroded_mask,dilate_element)

    #frame = dilated_mask


    # on the color-masked, blurred and morphed image apply the cv2.HoughCircles-method to detect circle-shaped objects 
    # min_dist may be too small and can result in false 'inner' circles being detected. Makind it bigger will prevent 
    # it from detecting a bunch of tomatoes close to each other individually.
    detected_circles = cv2.HoughCircles(dilated_mask, cv2.HOUGH_GRADIENT, 1, minDist=100, param1=100, param2=20, minRadius=20, maxRadius=150)
    circles = []
    if detected_circles is not None:
        for circle in detected_circles[0, :]:
            circles.append(circle)
    return circles

def _remove_false_circles(circles: list):
    """
    removes small circles with their center inside of a bigger circle
    """
    # sort corcles by radius 
    circles.sort(key=lambda x:[2])

    # indexes of circles to remove
    to_remove = set()
    for i in range(0, len(circles)-1):
        # check if center of this circle inside any other circle
        for j in range(i+1, len(circles)):
            if ((circles[i][0]-circles[j][0])**2+(circles[i][1]-circles[j][1])**2 <= circles[j][2]**2):
                to_remove.add(i)
    # removve the circles
    c = 0
    for i in to_remove:
        circles.pop(i-c)
        c+=1    
