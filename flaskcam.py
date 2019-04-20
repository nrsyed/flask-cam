import time

from flask import Flask, render_template, Response
from camera import Camera

app = Flask(__name__)

@app.route("/")
def index():
    #return "<h1>$uccess*</h1>"
    return render_template("index.html")

@app.route("/stream")
def stream():
    mimetype = "multipart/x-mixed-replace; boundary=frame-boundary"
    return Response(gen(), mimetype=mimetype)

def gen():
    cam = Camera()
    while True:
        frame = cam.get_frame()
        yield (b'--frame-boundary\r\nContent-Type: image/jpeg\r\n\r\n'
                + bytearray(frame) + b'\r\n'
        )
        time.sleep(.3)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
