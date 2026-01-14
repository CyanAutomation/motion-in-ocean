#!/usr/bin/python3

import argparse
import cv2
import io
import logging
import numpy as np
from threading import Condition
from flask import Flask, Response, render_template_string

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Parse command line arguments
parser = argparse.ArgumentParser(description="Picamera2 MJPEG streaming demo with options")
parser.add_argument("--resolution", type=str, help="Video resolution in WIDTHxHEIGHT format (default: 640x480)", default="640x480")
parser.add_argument("--edge_detection", action="store_true", help="Enable edge detection")
args = parser.parse_args()

# Parse resolution
resolution = tuple(map(int, args.resolution.split('x')))

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="{{ url_for('video_feed') }}" width="{width}" height="{height}" />
</body>
</html>
""".format(width=resolution[0], height=resolution[1])

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        if args.edge_detection:
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
    return render_template_string(PAGE)

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
    # picam2 = Picamera2()
    # picam2.configure(picam2.create_video_configuration(main={"size": resolution}))
    # picam2.start_recording(JpegEncoder(), FileOutput(output))

    try:
        app.run(host='0.0.0.0', port=8000, threaded=True)
    finally:
        # picam2.stop_recording()
        pass
