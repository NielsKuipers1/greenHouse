from camera import CameraReader
from cv2 import imwrite
import web_app
import threading
import schedule
import time

class Main():
    def __init__(self):
        self.cam = CameraReader()
    
    def take_picture(self, plant_id):
        frame = self.cam.read()
        imwrite(f"static/pic{plant_id}.jpg", frame)

def pic_testing(m):
    global i
    m.take_picture(i)
    print(f"New_picture {i}")
    i = ((i+1)%3) + 1
i = 1
if __name__ == "__main__":
    m = Main()
    # start a thread with web app
    threading.Thread(target=web_app.run_app, daemon=True).start()
    schedule.every(60).seconds.do(pic_testing, m)
    while True:
        schedule.run_pending()
        time.sleep(1)

