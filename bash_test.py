import numpy as np
from flask import Flask, render_template, redirect, url_for, session, request
from flask_socketio import SocketIO, emit, join_room
# from flask_cors import CORS
import random
import time
import threading
import rospy
from std_msgs.msg import String
from anytree import Node, RenderTree
from qt_robot_interface.srv import *
from qt_gesture_controller.srv import *
from std_msgs.msg import Float64MultiArray

# from emotion_card import *
# from object_action_card import *
# from emotion_card2 import *
# from emotion_card3 import *
# from flask_mysqldb import MySQL
# import mysql.connector as sql

# from interact_story import *
# from dice_rolling import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)



######################################################################################### Main ############################################################################################

if __name__ == '__main__':
    print("start")
    threading.Thread(target=lambda: rospy.init_node('app',
                                                    disable_signals=True)).start()  # it helps to start the rospy and ends terminal
    speechSay_pub = rospy.Publisher('/qt_robot/speech/say', String, queue_size=10)
    talktext_pub = rospy.Publisher('/qt_robot/behavior/talkText', String, queue_size=10)
    gesturePlay_pub = rospy.Publisher('/qt_robot/gesture/play', String, queue_size=10)
    emotionShow_pub = rospy.Publisher('/qt_robot/emotion/show', String, queue_size=10)
    audioPlay_pub = rospy.Publisher('/qt_robot/audio/play', String, queue_size=10)

    # gesturePlay_servc = rospy.ServiceProxy('/qt_robot/gesture/play', gesture_play)
    rospy.wait_for_service('/qt_robot/gesture/play')

    right_pub = rospy.Publisher('/qt_robot/right_arm_position/command', Float64MultiArray, queue_size=1)
    left_pub = rospy.Publisher('/qt_robot/left_arm_position/command', Float64MultiArray, queue_size=1)
    global f
    time_start = time.ctime()

    socketio.run(app, host='0.0.0.0', debug=True)  # connect to 192.168.100.2:5000 in web
    # socketio.run(app, host='localhost', debug=True)
    # record end time
    end = time.ctime()
    # f.write(str((end - time_start) / 60))
    # f.close()