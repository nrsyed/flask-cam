from datetime import datetime
import subprocess

import cv2
import numpy as np

class Camera():
    def __init__(self, src=0, device_name="video0", control_names=None):
        self.cap = cv2.VideoCapture(src)
        self.device_name = device_name

        if control_names is None:
            control_names = dict()

        # Control name strings (use uvcdynctrl -c for a given device to
        # obtain the correct names).
        auto_exposure = control_names.get("auto_exposure",  "Exposure, Auto")
        autofocus = control_names.get("autofocus", "Focus, Auto")
        brightness = control_names.get("brightness", "Brightness")
        contrast = control_names.get("contrast", "Contrast")
        exposure = control_names.get("exposure", "Exposure (Absolute)")
        focus = control_names.get("focus", "Focus (absolute)")
        saturation = control_names.get("saturation", "Saturation")
        zoom = control_names.get("zoom", "Zoom, Absolute")

        self.control_names = {
            "autofocus": autofocus,
            "brightness": brightness,
            "contrast": contrast,
            "exposure": exposure,
            "focus": focus,
            "saturation": saturation,
            "zoom": zoom
        }

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


    def set_control_value(self, control, value):
        # Full path to uvcdynctrl needed.
        control_name = self.control_names[control]
        subprocess.call(
            ["/usr/bin/uvcdynctrl", "-d", self.device_name, "-s", control_name, str(value)]
        )

    def get_control_value(self, control):
        control_name = self.control_names[control]
        value = subprocess.check_output(
            ["/usr/bin/uvcdynctrl", "-d", self.device_name, "-g", control_name]
        )
        value = int(value.decode("utf-8").strip())

        # Return a boolean for autofocus; otherwise, return raw int.
        if control == "autofocus":
            return value == 1
        return value

    def __del__(self):
        self.cap.release()
