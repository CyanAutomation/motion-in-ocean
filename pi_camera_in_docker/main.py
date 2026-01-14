#!/usr/bin/python3

import os
import cv2
import io
import logging
import numpy as np
from threading import Condition
from flask import Flask, Response, render_template

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Get configuration from environment variables
resolution_str = os.environ.get("RESOLUTION", "640x480")
edge_detection_str = os.environ.get("EDGE_DETECTION", "false")

# Parse resolution
try:
    resolution = tuple(map(int, resolution_str.split('x')))
except ValueError:
    logging.warning("Invalid RESOLUTION format. Using default 640x480.")
    resolution = (640, 480)

# Parse edge detection flag
edge_detection = edge_detection_str.lower() in ('true', '1', 't')

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        if edge_detection:
            # Convert the image buffer to a numpy array
            img_array = np.frombuffer(buf, dtype=np.uint8)
            # Decode the image array into an image
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            # Apply edge detection
            edges = cv2.Canny(img, 100, 200)
            # Encode the result back to JPEG
            _, buf = cv2.imencode('.jpg', edges)
            buf = buf.tobytes()
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

app = Flask(__name__)
output = StreamingOutput()

@app.route('/')
def index():
    return render_template("index.html", width=resolution[0], height=resolution[1])

def gen():
    try:
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        logging.warning('Removed streaming client: %s', str(e))

@app.route('/stream.mjpg')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": resolution}))
    
    # Start recording
    picam2.start_recording(JpegEncoder(), FileOutput(output))

    try:
        # Start the Flask app
        app.run(host='0.0.0.0', port=8000, threaded=True)
    finally:
        # Stop recording safely
        if picam2.started:
            picam2.stop_recording()