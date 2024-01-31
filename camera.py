import cv2
import threading
import queue
import numpy as np
from tensorflow.keras.models import load_model

class CameraReader(threading.Thread):
    def __init__(self, src=0):
        super(CameraReader, self).__init__()
        self.cap = cv2.VideoCapture(src)
        self.queue = queue.Queue()
        self.daemon = True
        self.start()
        self.model = load_model('tomato_model.h5')

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
        if len(circles) != 0:
            for circle in circles:
                frame = cv2.circle(frame, [int(circle[0]), int(circle[1])], int(circle[2]), (255,0, 0),thickness=2)
        if show: cv2.imshow("frame", frame)
        return [np.array([c[0],h-c[1]]-frame_center) for c in circles], frame
    
    def detect_ripe_tomatoes(self, frame, show=False):
        # Convert the frame to the HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        (fh, fw) = frame.shape[:2]
        # Define the lower and upper bounds for the red color (ripe tomatoes)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])

        # Create a mask for the red color
        mask = cv2.inRange(hsv, lower_red, upper_red)

        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        distance_list = []

        # Loop through the contours
        for contour in contours:
            # Calculate the area of each contour
            area = cv2.contourArea(contour)

            # Set a threshold for the area to filter out small contours
            if area > 350:
                # Draw a bounding box around the detected tomato
                x, y, w, h = cv2.boundingRect(contour)

                # Add this tomatoes location data to the list
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                distance_list.append(np.array([x-fw/2, fh/2-y]))
                # Extract the tomato from the frame and resize it to the size the model expects
                tomato = frame[y:y+h, x:x+w]
                tomato = cv2.resize(tomato, (224, 224))

                # Normalize the image to 0-1 range
                tomato = tomato / 255.0

                # Add an extra dimension for the batch size
                tomato = np.expand_dims(tomato, axis=0)

                # Use the model to predict whether the tomato is ripe or unripe
                prediction = self.model.predict(tomato)[0][0]

                # The prediction is a number between 0 and 1 due to the sigmoid activation function
                # We can convert this to a binary label
                label = "Ripe" if prediction > 0.6 else "Unripe"
                # Color is in BGR instead of RGB
                color = (36, 255, 12) if prediction > 0.6 else (12, 40, 255)

                # Add position info to the label
                # location_str = " X:" + str(x) + " Y:" + str(y) + " W:" + str(w) + " H:"+ str(h)
                # label += location_str

                # Draw the label on the frame
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Display the result
        if show: cv2.imshow("Ripe Tomato Detection", frame)
        return distance_list, frame

def _detect_red_circles(frame):
    """
    returns a list of circles [x, y, radius] of tomatoes
    """

    blur = cv2.GaussianBlur(frame, (13,13), 0)
    hsv_conv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # because hue wraps up and to extract as many "red objects" as possible, define lower and upper boundaries for brighter and for darker red shades
    bright_red_lower_bounds = (0, 100, 0)
    bright_red_upper_bounds = (10, 255, 255)
    bright_red_mask = cv2.inRange(hsv_conv_img, bright_red_lower_bounds, bright_red_upper_bounds)

    dark_red_lower_bounds = (160, 100, 50)
    dark_red_upper_bounds = (200, 255, 255)
    dark_red_mask = cv2.inRange(hsv_conv_img, dark_red_lower_bounds, dark_red_upper_bounds)

    # after masking the red shades out, I add the two images 
    weighted_mask = cv2.addWeighted(bright_red_mask, 1.0, dark_red_mask, 1.0, 0.0)

    # then the result is blurred
    blurred_mask = cv2.GaussianBlur(weighted_mask,(9,9),3,3)

    # some morphological operations (closing) to remove small blobs 
    erode_element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilate_element = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    eroded_mask = cv2.erode(blurred_mask,erode_element)
    dilated_mask = cv2.dilate(eroded_mask,dilate_element)

    frame = dilated_mask


    # on the color-masked, blurred and morphed image apply the cv2.HoughCircles-method to detect circle-shaped objects 
    # min_dist may be too small and can result in false 'inner' circles being detected. Makind it bigger will prevent 
    # it from detecting a bunch of tomatoes close to each other individually.
    detected_circles = cv2.HoughCircles(dilated_mask, cv2.HOUGH_GRADIENT, 1, minDist=100, param1=100, param2=30, minRadius=20, maxRadius=150)
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
