import cv2
import time

def detect_red_tomatos(frame):

    hsv_conv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

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


    # on the color-masked, blurred and morphed image apply the cv2.HoughCircles-method to detect circle-shaped objects 
    detected_circles = cv2.HoughCircles(dilated_mask, cv2.HOUGH_GRADIENT, 1, 150, param1=100, param2=20, minRadius=20, maxRadius=200)
    centers = []
    if detected_circles is not None:
        for circle in detected_circles[0, :]:
            circled_orig = cv2.circle(frame, [int(circle[0]), int(circle[1])], int(circle[2]), (0,255,0),thickness=3)
            centers.append(circle[2])
        cv2.imshow("original", circled_orig)
    else:
        pass
        cv2.imshow("original", frame)
    return centers

def demo_run():
    prev = 0

    cap = cv2.VideoCapture(0)

    while(True):
        ret, frame = cap.read()

        if not ret:
            print("Error: Couldn't read frame")
            break

        detect_red_tomatos(frame)
        print(time.time() - prev)
        prev = time.time()

    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

demo_run()