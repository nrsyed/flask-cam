import functools
from ipaddress import ip_address, ip_network
import os
import subprocess
import sys
import syslog
import time

from flask import Flask, jsonify, render_template, Response, request, current_app

from camera import Camera
from password import authenticate_user

app = Flask(__name__)
cam = Camera()

@app.before_first_request
def initialize():
    current_app.delay = 0.1

def unauthorized():
    return Response(
        "Credential error", 401, {"WWW-Authenticate": "Basic realm='Login Required'"}
    )

def requires_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Running a script from Python with subprocess via gunicorn seems to
        # present many issues, including lack of PATH and inability to resolve
        # paths even when `shell=True` is passed. Instead, write IP/mask to file
        # on network up and periodically via network and cron jobs; we check
        # the contents of said file here to obtain the local IP and subnet mask.
        # `local_network` file contains IP/subnet in format
        # `XXX.XXX.XXX.XXX/YYY.YYY.YYY.YYY`.

        subnet = None
        filepath = os.path.join(sys.path[0], "tmp/local_network")
        try:
            with open(filepath, "r") as file_:
                local_ip_and_mask = file_.readline().strip()
            subnet = ip_network(local_ip_and_mask, strict=False)
        except Exception as e:
            syslog.syslog(str(e))

        # Get IP address of requester using nginx header. Do not require
        # authentication for requests originating on the local network.
        remote_addr = request.environ.get("HTTP_X_FORWARDED_FOR")
        syslog.syslog("request from {}".format(remote_addr))
        if remote_addr is None or subnet is None or ip_address(remote_addr) not in subnet:
            auth = request.authorization
            if not auth or not authenticate_user(auth.username, auth.password, "users"):
                return unauthorized()
        return func(*args, **kwargs)
    return wrapper 

@app.route("/")
@requires_auth
def index():
    remote_addr = request.environ.get("HTTP_X_FORWARDED_FOR")
    return render_template("index.html")

@app.route("/stream")
def stream():
    mimetype = "multipart/x-mixed-replace; boundary=frame-boundary"
    return Response(gen(), mimetype=mimetype)

@app.route("/get", methods=["GET"])
def get():
    controls = [
        "autofocus",
        "brightness",
        "contrast",
        "exposure",
        "focus",
        "saturation",
        "zoom"
    ]

    control_values = dict()
    for control in controls:
        control_values[control] = cam.get_control_value(control)
    control_values["delay"] = current_app.delay
    return jsonify(control_values)

@app.route("/submit", methods=["POST"])
def submit():
    brightness = int(request.form["slider-brightness"])
    contrast = int(request.form["slider-contrast"])
    exposure = int(request.form["slider-exposure"])
    focus = int(request.form["slider-focus"])
    zoom = int(request.form["slider-zoom"])
    current_app.delay = float(request.form["num-delay"])

    cam.set_control_value("brightness", brightness)
    cam.set_control_value("contrast", contrast)
    cam.set_control_value("exposure", exposure)
    cam.set_control_value("focus", focus)
    cam.set_control_value("zoom", zoom)
    return "ok"

def gen():
    while True:
        frame = cam.get_frame()
        yield (b'--frame-boundary\r\nContent-Type: image/jpeg\r\n\r\n'
                + bytearray(frame) + b'\r\n'
        )
        with app.app_context():
            time.sleep(current_app.delay)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
