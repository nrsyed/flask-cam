from os import path
from sys import path
from syslog import syslog
from functools import wraps
from time import sleep as time_sleep

from ipaddress import ip_address, ip_network

from werkzeug import exceptions
from flask import (
    Flask,
    Response,
    current_app,
    jsonify,
    request,
    render_template
)

from camera import Camera
from password import authenticate_user


app = Flask(__name__)
cam = Camera()

CONTENT_DATA = '--frame-boundary\r\nContent-Type: image/jpeg\r\n\r\n%s\r\n'


@app.before_first_request
def initialize():
    current_app.delay = 0.1


def unauthorized():
    return Response("Credential error", 401, {"WWW-Authenticate": "Basic realm='Login Required'"})


def requires_auth(func):
    """
    Decorator for routes that require authentication.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Running a script from Python with subprocess via gunicorn seems to
        # present many issues, including lack of PATH and inability to resolve
        # paths even when `shell=True` is passed. Instead, write IP/mask to file
        # on network up and periodically via network and cron jobs; we check
        # the contents of said file here to obtain the local IP and subnet mask.
        # `local_network` file contains IP/subnet in format
        # `XXX.XXX.XXX.XXX/YYY.YYY.YYY.YYY`.

        subnet = None
        # filepath = path.join(path[0], "tmp/local_network")
        filepath = "/tmp/local_network"
        try:
            with open(filepath, "r") as file_:
                local_ip_and_mask = file_.readline().strip()
            subnet = ip_network(local_ip_and_mask, strict=False)
        except Exception as e:
            syslog(str(e))

        # Get IP address of requester using nginx header. Do not require
        # authentication for requests originating on the local network.
        remote_addr = request.environ.get("HTTP_X_FORWARDED_FOR")
        syslog("request from {}".format(remote_addr))
        if remote_addr is None or subnet is None or ip_address(remote_addr) not in subnet:
            auth = request.authorization
            if not auth or not authenticate_user(auth.username, auth.password, "users"):
                return unauthorized()
        return func(*args, **kwargs)
    return wrapper 


@app.route("/")
# @requires_auth
def index():
    return render_template("index.html")


@app.route("/kiosk")
# @requires_auth
def kiosk():
    return render_template("kiosk.html")


@app.errorhandler(exceptions.BadRequest)
def handle_bad_request(e):
    return f'bad request: {e}', 400


@app.route("/get", methods=["GET"])
def get():
    controls = [
        "autoexposure",
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
    """
    Route called when submitting the control form from the web interface
    to update camera device and application control values.
    """

    autoexposure = request.form["autoexposure"]
    autofocus = request.form["autofocus"]
    brightness = int(request.form["brightness"])
    contrast = int(request.form["contrast"])
    exposure = int(request.form["exposure"])
    focus = int(request.form["focus"])
    zoom = int(request.form["zoom"])
    current_app.delay = float(request.form["delay"])

    cam.set_control_value("autoexposure", {"true": 3, "false": 1}[autoexposure])
    cam.set_control_value("autofocus", {"true": 1, "false": 0}[autofocus])
    cam.set_control_value("brightness", brightness)
    cam.set_control_value("contrast", contrast)
    cam.set_control_value("exposure", exposure)
    cam.set_control_value("focus", focus)
    cam.set_control_value("zoom", zoom)

    # TODO: response
    return "ok"


@app.route("/stream", methods=["GET", "POST"])
def stream():
    mimetype = "multipart/x-mixed-replace; boundary=frame-boundary"

    if request.method == "POST":
        cam.set_fps(int(request.form["fps"]))
        cam.screen_width = int(request.form["width"])
        cam.screen_height = int(request.form["height"])

    return Response(gen(), mimetype=mimetype)


def gen():
    """
    Generator to continuously grab and yield frames from the Camera object.
    """

    while True:
        frame = cam.get_frame()
        yield (b'--frame-boundary\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(frame) + b'\r\n')
        with app.app_context():
            # Add nominal delay between frames to prevent performance issues.
            time_sleep(current_app.delay)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
