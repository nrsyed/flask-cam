from functools import wraps
import time

from flask import Flask, render_template, Response, request
from camera import Camera

app = Flask(__name__)
cam = Camera()
delay = 0.3

def check_auth(username, password):
    return username == "dexter" and password == "omelet"

def authenticate():
    return Response(
        "Credential error", 401, {"WWW-Authenticate": "Basic realm='Login Required'"}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/")
@requires_auth
def index():
    #return "<h1>$uccess*</h1>"
    return render_template("index.html")

@app.route("/stream")
def stream():
    mimetype = "multipart/x-mixed-replace; boundary=frame-boundary"
    return Response(gen(), mimetype=mimetype)

@app.route("/submit", methods=["POST"])
def submit():
    global delay
    focus = int(request.form["slider-focus"])
    zoom = int(request.form["slider-zoom"])
    delay = float(request.form["num-delay"])
    cam.set_focus(focus)
    cam.set_zoom(zoom)
    return "ok"

def gen():
    #cam = Camera()
    while True:
        frame = cam.get_frame()
        yield (b'--frame-boundary\r\nContent-Type: image/jpeg\r\n\r\n'
                + bytearray(frame) + b'\r\n'
        )
        time.sleep(delay)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
