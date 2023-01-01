# much of this is from a modified blog post I read here:
# https://towardsdatascience.com/video-streaming-in-web-browsers-with-opencv-flask-93a38846fe00
# as well as a stack exchange post I read here:
# https://stackoverflow.com/questions/51079338/audio-livestreaming-with-python-flask
# stuck all this code together to get something relatively useful

"""
work I did do here was to refactor some of the SE code immensely to make it more readable and figure out wtf it's
doing, and also stitching of the two things together.


trying to figure this out, using this linux command to record from webcam

ffmpeg -f alsa -i default -itsoffset 00:00:00 -f video4linux2  -i /dev/video0 out.avi

"""
import os
import signal

from flask import Flask, render_template, Response
import cv2
from subprocess import Popen, PIPE
from datetime import datetime

app = Flask(__name__)
print('engage!')

# necessary vars
recording_process = None


@app.route('/')
def index():
    if recording_process:
        return render_template('index.html', camera_status="Click to stop recording")
    else:
        return render_template('index.html', camera_status="Click to start recording")

@app.route('/toggle')
def toggle():
    global recording_process
    now = datetime.utcnow()

    print(os.getcwd())
    if recording_process is None:
        print(f"starting video at {str(now)}")
        file_path = os.path.join(os.getcwd(), "static")

        recording_process = Popen(
            f'exec ffmpeg -f alsa -i default -itsoffset 00:00:00 -f video4linux2  -i /dev/video0 {file_path}/{str(now.timestamp())}.avi',
            stdin=PIPE,
            stdout=PIPE,
            shell=True,
            preexec_fn=os.setsid
        )
    else:
        print('Killing camera feed')
        recording_process.terminate()
        recording_process = None
    return index()

def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, threaded=True,port=5000)
