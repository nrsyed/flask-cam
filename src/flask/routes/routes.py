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

from src.flask.camera.camera import Camera
from src.auth.auth_manager import authenticate_user


flask_application = Flask(__name__)
camera = Camera()


@flask_application.before_first_request
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


@flask_application.route("/")
@requires_auth
def index():
    return render_template("index.html")


@flask_application.route("/kiosk")
@requires_auth
def kiosk():
    return render_template("kiosk.html")


@flask_application.errorhandler(exceptions.BadRequest)
def handle_bad_request(e):
    return f'bad request: {e}', 400


@flask_application.route("/get", methods=["GET"])
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
        control_values[control] = camera.get_control_value(control)
    control_values["delay"] = current_app.delay
    return jsonify(control_values)


@flask_application.route("/submit", methods=["POST"])
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

    camera.set_control_value("autoexposure", {"true": 3, "false": 1}[autoexposure])
    camera.set_control_value("autofocus", {"true": 1, "false": 0}[autofocus])
    camera.set_control_value("brightness", brightness)
    camera.set_control_value("contrast", contrast)
    camera.set_control_value("exposure", exposure)
    camera.set_control_value("focus", focus)
    camera.set_control_value("zoom", zoom)

    # TODO: response
    return "ok"


@flask_application.route("/stream", methods=["GET", "POST"])
def stream():
    mimetype = "multipart/x-mixed-replace; boundary=frame-boundary"

    if request.method == "POST":
        camera.set_fps(int(request.form["fps"]))
        camera.screen_width = int(request.form["width"])
        camera.screen_height = int(request.form["height"])

    return Response(gen(), mimetype=mimetype)


def gen():
    """
    Generator to continuously grab and yield frames from the Camera object.
    """

    while True:
        frame = camera.get_frame()
        yield (b'--frame-boundary\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(frame) + b'\r\n')
        with flask_application.app_context():
            # Add nominal delay between frames to prevent performance issues.
            time_sleep(current_app.delay)
