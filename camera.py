from datetime import datetime
import subprocess

import cv2
import numpy as np


class Camera():
    """
    Class for reading frames from or getting/setting control values for a camera.
    """

    def __init__(self, src=0, device_name="video0", control_names=None):
        """
        :param src: VideoCapture source device id or filename.
        :type src: int | str
        :param device_name: Camera device name (use `uvcdynctrl --list`).
        :type device_name: str
        :param control_names: Dictionary mapping control names used by the
            Flask application/web interface to the control names used by
            the device (use `uvcdynctrl --clist` to obtain a list).
        :type control_names: dict
        """

        self.cap = cv2.VideoCapture(src)
        self.device_name = device_name

        if control_names is None:
            control_names = dict()

        autoexposure = control_names.get("autoexposure",  "Exposure, Auto")
        autofocus = control_names.get("autofocus", "Focus, Auto")
        brightness = control_names.get("brightness", "Brightness")
        contrast = control_names.get("contrast", "Contrast")
        exposure = control_names.get("exposure", "Exposure (Absolute)")
        focus = control_names.get("focus", "Focus (absolute)")
        saturation = control_names.get("saturation", "Saturation")
        zoom = control_names.get("zoom", "Zoom, Absolute")

        self.control_names = {
            "autoexposure": autoexposure,
            "autofocus": autofocus,
            "brightness": brightness,
            "contrast": contrast,
            "exposure": exposure,
            "focus": focus,
            "saturation": saturation,
            "zoom": zoom
        }


    def get_frame(self):
        """
        Read a frame from the VideoCapture object stream, superimpose a
        timestamp on the frame, and return it encoded as a JPG.
        """

        grabbed, frame = self.cap.read()

        if not grabbed:
            self.cap.release()

        # Resize frame to a desired size; since frames are not compressed
        # before passing them to the web frontend, large frame sizes may reduce
        # speed/performance.
        # TODO: add desired frame size as a parameter?
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
        """
        Call uvcdynctrl in a subprocess to set a control value.

        :param control: Control name/type (e.g., "zoom").
        :type control: str
        :param value: New value to set.
        :type value: int
        """

        # Full path to uvcdynctrl needed.
        control_name = self.control_names[control]
        subprocess.call(
            [
                "/usr/bin/uvcdynctrl", "-d", self.device_name, "-s",
                control_name, str(value)
            ]
        )


    def get_control_value(self, control):
        """
        Call uvcdynctrl in a subprocess to get the current value of a control.

        :param control: Control name/type (e.g., "zoom").
        :type control: str
        :return: The control value (as an integer for controls that can take on
            a range of discrete values, or as a boolean for controls that can
            be toggled on/off).
        :rtype: int | str
        """

        control_name = self.control_names[control]
        value = subprocess.check_output(
            ["/usr/bin/uvcdynctrl", "-d", self.device_name, "-g", control_name]
        )
        value = int(value.decode("utf-8").strip())

        # Return a boolean for autofocus and autoexposure; otherwise,
        # return raw int.
        if control == "autofocus":
            return value == 1
        elif control == "autoexposure":
            # Options are 1 (manual mode) and 3 (aperture priority mode).
            return value == 3
        return value


    def __del__(self):
        self.cap.release()
