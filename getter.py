from datetime import datetime
import multiprocessing.connection
import os
import socket
import threading

import cv2

class VideoGet:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self.get_frames, args=(), daemon=True).start()
        return self

    def get_frames(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                grabbed, frame = self.cap.read()
                if grabbed:
                    height, width = frame.shape[:2]
                    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    cv2.putText(
                        frame, timestamp, (int(0.02 * width), int(0.98 * height)),
                        cv2.FONT_HERSHEY_COMPLEX_SMALL, .7, (250, 250, 250), 1, 20, False
                    )
                self.grabbed, self.frame = grabbed, frame

    def stop(self):
        self.stopped = True

    def __del__(self):
        self.cap.release()

def main():
    # Find a free port to listen on.
    sock = socket.socket()
    sock.bind(("", 0))
    listen_port = sock.getsockname()[1]
    sock.close()

    # Write the port number to a file.
    home_dir = os.path.expanduser("~")
    filepath = os.path.join(home_dir, ".cam_server")
    with open(filepath, "w") as file_:
        file_.write(str(listen_port))

    stream = VideoGet(src=0).start()
    listen_on = ("localhost", listen_port)
    listener = multiprocessing.connection.Listener(listen_on)
    while True:
        if stream.stopped:
            break
        ip_addr, port = listener.accept().recv()
        #print("{}:{}".format(ip_addr, port))
        sender = multiprocessing.connection.Client((ip_addr, port))
        sender.send(stream.frame)
    listener.close()

if __name__ == "__main__":
    main()
