import functools
import syslog
import time

from flask import Flask, render_template, Response, request, current_app

from camera import Camera
from password import authenticate_user

app = Flask(__name__)
cam = Camera()

@app.before_first_request
def initialize():
    current_app.delay = 0.2

def unauthorized():
    return Response(
        "Credential error", 401, {"WWW-Authenticate": "Basic realm='Login Required'"}
    )

def requires_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticate_user(auth.username, auth.password, "users"):
            return unauthorized()
        return func(*args, **kwargs)
    return wrapper 

@app.route("/")
@requires_auth
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    mimetype = "multipart/x-mixed-replace; boundary=frame-boundary"
    return Response(gen(), mimetype=mimetype)

@app.route("/submit", methods=["POST"])
def submit():
    focus = int(request.form["slider-focus"])
    zoom = int(request.form["slider-zoom"])
    current_app.delay = float(request.form["num-delay"])

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
