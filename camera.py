from datetime import datetime
import subprocess

import cv2
import numpy as np

class Camera():
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        #self.cap.set(cv2.CAP_PROP_FOCUS, 5)
        #self.cap.set(14, 0)

    def get_frame(self):
        grabbed, frame = self.cap.read()

        if not grabbed:
            self.cap.release()

        frame = cv2.resize(frame, (640, 480))
        height, width = frame.shape[:2]
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        cv2.putText(
            frame, timestamp, (int(0.02 * width), int(0.98 * height)),
            cv2.FONT_HERSHEY_COMPLEX_SMALL, .7, (250, 250, 250), 1, 20, False
        )
        frame_jpg = cv2.imencode(".jpg", frame)[1]
        return frame_jpg

    def set_focus(self, focus):
        subprocess.call(
            ["uvcdynctrl", "-d", "video0", "-s", "Focus (absolute)", str(focus)]
        )

    def set_zoom(self, zoom):
        subprocess.call(
            ["uvcdynctrl", "-d", "video0", "-s", "Zoom, Absolute", str(zoom)]
        )

    def __del__(self):
        self.cap.release()
