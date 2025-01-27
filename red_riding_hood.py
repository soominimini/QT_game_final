import numpy as np
from flask import Flask, render_template, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room
import random
import time
import threading
# import rospy
# from std_msgs.msg import String
# from qt_robot_interface.srv import *
# from qt_gesture_controller.srv import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


global talktext_pub
global speechSay_pub
global emotionShow_pub
global gesturePlay_pub
global audioPlay_pub
global gesturePlay_servc



@socketio.on('red_riding_first')
def red_riding_first():
    # Display two characters. Becomes the main character of the story
    # rospy.sleep(1.0)
    # global talktext_pub
    print("first_talk_robot_interactive")
    # talktext_pub.publish("Lets start the story!")


def interact_main():
    threading.Thread(target=lambda: rospy.init_node('red_riding',
                                                    disable_signals=True)).start()  # it helps to start the rospy and ends terminal
    global talktext_pub
    global speechSay_pub
    global emotionShow_pub
    global gesturePlay_pub
    global audioPlay_pub
    global gesturePlay_servc
    speechSay_pub = rospy.Publisher('/qt_robot/speech/say', String, queue_size=10)
    talktext_pub = rospy.Publisher('/qt_robot/behavior/talkText', String, queue_size=10)
    audioPlay_pub = rospy.Publisher('/qt_robot/audio/play', String, queue_size=10)
    emotionShow_pub = rospy.Publisher('/qt_robot/emotion/show', String, queue_size=10)
    gesturePlay_pub = rospy.Publisher('/qt_robot/gesture/play', String, queue_size=10)
    gesturePlay_servc = rospy.ServiceProxy('/qt_robot/gesture/play', gesture_play)

