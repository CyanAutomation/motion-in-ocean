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
from picamera2.array import MappedArray

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

def apply_edge_detection(request):
    with MappedArray(request, "main") as m:
        # Convert to grayscale
        grey = cv2.cvtColor(m.array, cv2.COLOR_BGR2GRAY)
        # Apply Canny edge detection
        edges = cv2.Canny(grey, 100, 200)
        # Convert back to BGR so it can be encoded as JPEG
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        # Copy the result back to the mapped array
        np.copyto(m.array, edges_bgr)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
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
    picam2 = None
    try:
        picam2 = Picamera2()
        # Configure for BGR format for opencv
        video_config = picam2.create_video_configuration(main={"size": resolution, "format": "BGR888"})
        picam2.configure(video_config)

        if edge_detection:
            picam2.pre_callback = apply_edge_detection
        
        # Start recording
        picam2.start_recording(JpegEncoder(), FileOutput(output))

        # Start the Flask app
        app.run(host='0.0.0.0', port=8000, threaded=True)
    finally:
        # Stop recording safely
        if picam2 and picam2.started:
            picam2.stop_recording()