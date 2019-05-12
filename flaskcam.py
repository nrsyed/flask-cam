import multiprocessing.connection
import os
import socket
import subprocess
import threading
import time

from flask import Flask, render_template, Response, request, current_app
#from camera import Camera
import cv2

app = Flask(__name__)

@app.before_first_request
def init():
    # Determine which port the camera server is listening on.
    home_dir = os.path.expanduser("~")
    filepath = os.path.join(home_dir, ".cam_server")
    with open(filepath, "r") as file_:
        cam_server_port = int(file_.read())

    current_app.send_to = ("localhost", cam_server_port)
    current_app.delay = 2.0

@app.route("/")
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
    set_focus(focus)
    #cam.set_zoom(zoom)
    return "ok"

def set_focus(focus):
    subprocess.call(
        ["uvcdynctrl", "-d", "video0", "-s", "Focus (absolute)", str(focus)]
    )

def gen():
        #delay = current_app.delay
    #frame_getter = FrameGet().start()

    while True:
        frame = get_from_server()
        yield (b'--frame-boundary\r\nContent-Type: image/jpeg\r\n\r\n'
                + bytearray(frame) + b'\r\n'
        )

def get_from_server():
    with app.app_context():
        send_to = current_app.send_to

    # Find free socket (port) to listen on.
    sock = socket.socket()
    sock.bind(("",0))
    recv_port = sock.getsockname()[1]
    sock.close()
    listen_on = ("localhost", recv_port)
    frames = open("stream.jpg", "wb+")
    listener = multiprocessing.connection.Listener(listen_on)

    # With our request, send the address we're listening on.
    sender = multiprocessing.connection.Client(send_to)
    sender.send(listen_on)

    # The cam server will send a frame in response.
    frame = listener.accept().recv()
    cv2.imwrite("stream.jpg", frame)
    return frames.read()

if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True)
