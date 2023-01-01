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
import time

from flask import Flask, render_template, Response
from flask import send_from_directory

from subprocess import Popen, PIPE
from datetime import datetime

app = Flask(__name__, static_folder="static")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = "static"

# necessary vars
recording_process = None


@app.route('/static/<path:filename>/get')
def download_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), "static"),
                               filename, as_attachment=True)


@app.route('/static/<path:filename>/delete')
def delete_video(filename):
    print('deleting!')

    os.remove(f"static/{filename}")
    return index()


@app.route('/')
def index():
    current_files = [file for file in os.listdir("static") if file != "bootstrap"]  # awful hardcode!
    print(current_files)

    if recording_process:
        return render_template('index.html',
                               status="btn-danger",
                               current_files=current_files,
                               camera_status="Click to stop recording")
    else:
        return render_template('index.html',
                               current_files=current_files,
                               status="btn-primary",
                               camera_status="Click to start recording")


@app.route('/toggle')
def toggle():
    global recording_process
    now = datetime.utcnow()

    if recording_process is None:
        print(f"starting video at {str(now)}")
        file_path = os.path.join(os.getcwd(), "static")

        date_time = now.strftime("%m-%d-%Y_%H:%M:%S")
        cmd = f'exec ffmpeg -f alsa -i default -itsoffset 00:00:00 -f video4linux2  -i /dev/video0 {file_path}/{date_time}.avi'
        print(cmd)
        recording_process = Popen(
            cmd,
            stdin=PIPE,
            stdout=PIPE,
            shell=True,
            preexec_fn=os.setsid
        )
    else:
        print('Killing camera feed')
        time.sleep(1)
        recording_process.terminate()
        recording_process = None
    return index()


if __name__ == '__main__':
    app.run(debug=True,
            threaded=True,
            port=5000)
