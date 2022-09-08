from distutils.util import strtobool
from time import sleep as time_sleep

from flask import (
    Flask,
    Response,
    current_app,
    jsonify,
    request,
    render_template
)

from src.flask.camera.camera import Camera
from src.flask.statistic.anxiety_statistic import AnxietyStatistic

from project import TEMPLATES_DIR_PATH, STATIC_DIR_PATH


flask_application = Flask(__name__, template_folder=TEMPLATES_DIR_PATH.__str__(), static_folder=STATIC_DIR_PATH)

camera = Camera()
anxiety_statistic = AnxietyStatistic(saved_data=[])


@flask_application.before_first_request
def initialize():
    current_app.delay = 0.1


@flask_application.route("/")
# @requires_auth
def index():
    return render_template("index.html")


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


@flask_application.route('/statistic', methods=['POST', 'GET'])
def load_statistic_data():
    if request.method == 'POST':
        post_data = [bool(strtobool(elem)) for elem in request.get_json(force=True)]
        anxiety_statistic.add_anxiety_statistic(post_data)
        return jsonify({'message': 'success'})

    if request.method == 'GET':
        return jsonify(anxiety_statistic.get_anxiety_statistic)

    return jsonify({'message': 'error'})
