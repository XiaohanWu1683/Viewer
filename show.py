# coding:utf8
import numpy as np
import codecs
import urllib
import json
import cv2
import pandas as pd
import requests
import bs4
import imutils
import matplotlib
# matplotlib.use("Agg")
from os import listdir
import matplotlib.image as mpimg
import matplotlib.pylab as plt
from matplotlib.pyplot import savefig
import copy
from werkzeug.test import EnvironBuilder
from flask import Flask, render_template, Response, request, session, flash, g, current_app
from flask_wtf import FlaskForm, RecaptchaField
from wtforms.validators import DataRequired, NumberRange
from wtforms.fields import (StringField, PasswordField, DateField, BooleanField,
                            SelectField, SelectMultipleField, TextAreaField,
                            RadioField, IntegerField, DecimalField, SubmitField)


class VideoCamera(object):
    def get_page_urls(self, url):  # 字符串处理
        json_file = []
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.text, "html5lib")
        page_info = [a.attrs.get('href') for a in soup.select('li a')]
        for i in page_info:
            if i[-4:] == 'json':
                json_file.append(i)
        return json_file

    def get_position(self, junction, frame):
        x = []
        y = []
        for a, i in enumerate(range(frame.shape[0])):
            y.append(int(frame[a].get(junction).get('x')))
            x.append(int(frame[a].get(junction).get('y')))
        return x, y

    def __init__(self, data_number):
        url = 'http://www.cadietrich.net/reports/legotracker/database/'
        json_file = self.get_page_urls(url)
        data_num = data_number  # 输入视频号码
        s = json_file[int(data_num)]
        read_json = urllib.request.urlopen(url + s)
        data = json.loads(read_json.read().decode('utf8'))
        frames = np.array(data[u'frames'])
        video = data[u'video']
        play_id = np.array(data[u'play_id'])
        #         print(play_id)
        timestamp = np.array(data[u'timestamp'])
        junctions = ['left_ankle', 'left_elbow', 'left_hip', 'left_knee', 'left_shoulder', 'left_wrist',
                     'right_ankle', 'right_elbow', 'right_hip', 'right_knee', 'right_shoulder', 'right_wrist'
                     ]  # 关节名称

        self.left_ax, self.left_ay = self.get_position('left_ankle', frames)
        self.left_ex, self.left_ey = self.get_position('left_elbow', frames)
        self.left_hx, self.left_hy = self.get_position('left_hip', frames)
        self.left_kx, self.left_ky = self.get_position('left_knee', frames)
        self.left_sx, self.left_sy = self.get_position('left_shoulder', frames)
        self.left_wx, self.left_wy = self.get_position('left_wrist', frames)
        self.right_ax, self.right_ay = self.get_position('right_ankle', frames)
        self.right_ex, self.right_ey = self.get_position('right_elbow', frames)
        self.right_hx, self.right_hy = self.get_position('right_hip', frames)
        self.right_kx, self.right_ky = self.get_position('right_knee', frames)
        self.right_sx, self.right_sy = self.get_position('right_shoulder', frames)
        self.right_wx, self.right_wy = self.get_position('right_wrist', frames)

        download_video = urllib.request.FancyURLopener()
        download_video.retrieve(video, 'video.mp4')

        camera = cv2.VideoCapture('video.mp4')
        self.video = camera
        self._countFrame = 0
        self.color1 = (0, 0, 255)
        self.color2 = (255, 0, 0)
        self.center = 5
        self.thickness = 999

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        frame1 = copy.deepcopy(frame)
        frame2 = frame
        cv2.line(frame2, (self.left_ax[self._countFrame], self.left_ay[self._countFrame]),
                 (self.left_kx[self._countFrame], self.left_ky[self._countFrame]), self.color1, 2, 3)
        cv2.line(frame2, (self.left_hx[self._countFrame], self.left_hy[self._countFrame]),
                 (self.left_kx[self._countFrame], self.left_ky[self._countFrame]), self.color1, 2, 3)
        cv2.line(frame2, (self.left_sx[self._countFrame], self.left_sy[self._countFrame]),
                 (self.left_ex[self._countFrame], self.left_ey[self._countFrame]), self.color1, 2, 3)
        cv2.line(frame2, (self.left_wx[self._countFrame], self.left_wy[self._countFrame]),
                 (self.left_ex[self._countFrame], self.left_ey[self._countFrame]), self.color1, 2, 3)

        cv2.line(frame2, (self.right_ax[self._countFrame], self.right_ay[self._countFrame]),
                 (self.right_kx[self._countFrame], self.right_ky[self._countFrame]), self.color1, 2, 3)
        cv2.line(frame2, (self.right_hx[self._countFrame], self.right_hy[self._countFrame]),
                 (self.right_kx[self._countFrame], self.right_ky[self._countFrame]), self.color1, 2, 3)
        cv2.line(frame2, (self.right_sx[self._countFrame], self.right_sy[self._countFrame]),
                 (self.right_ex[self._countFrame], self.right_ey[self._countFrame]), self.color1, 2, 3)
        cv2.line(frame2, (self.right_wx[self._countFrame], self.right_wy[self._countFrame]),
                 (self.right_ex[self._countFrame], self.right_ey[self._countFrame]), self.color1, 2, 3)

        cv2.circle(frame2, (self.left_ax[self._countFrame], self.left_ay[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.left_ex[self._countFrame], self.left_ey[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.left_hx[self._countFrame], self.left_hy[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.left_kx[self._countFrame], self.left_ky[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.left_sx[self._countFrame], self.left_sy[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.left_wx[self._countFrame], self.left_wy[self._countFrame]), self.center, self.color2,
                   2, self.thickness)

        cv2.circle(frame2, (self.right_ax[self._countFrame], self.right_ay[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.right_ex[self._countFrame], self.right_ey[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.right_hx[self._countFrame], self.right_hy[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.right_kx[self._countFrame], self.right_ky[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.right_sx[self._countFrame], self.right_sy[self._countFrame]), self.center, self.color2,
                   2, self.thickness)
        cv2.circle(frame2, (self.right_wx[self._countFrame], self.right_wy[self._countFrame]), self.center, self.color2,
                   2, self.thickness)

        self._countFrame = self._countFrame + 1
        hmerge = np.hstack((frame1, frame2))
        hmerge = imutils.resize(hmerge, width=1000)
        ret, jpeg = cv2.imencode('.jpg', hmerge)
        return jpeg.tobytes()


class Loginform(FlaskForm):
    video_name = SelectField('Please choose video name', choices=[
        ('0', 'First'),
        ('1', 'Second'),
        ('2', 'Third'),
        ('3', 'Forth')
    ])


app = Flask(__name__)



app.config.update(
    RECAPTCHA_PUBLIC_KEY='6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J',
    RECAPTCHA_PRIVATE_KEY='6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu',
    RECAPTCHA_PARAMETERS={'hl': 'zh', 'render': 'explicit'},
    RECAPTCHA_DATA_ATTRS={'theme': 'dark'}
)


@app.route('/', methods=("GET", "POST"))
def index():
    form = Loginform()
    session['value'] = form.video_name.data
    return render_template('index.html', form=form)


def gen(camera):
    while True:
        generated_frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + generated_frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    iput_val = session.pop('value', 1)
    return Response(gen(VideoCamera(int( iput_val ))),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


app.secret_key = '1234567'

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
