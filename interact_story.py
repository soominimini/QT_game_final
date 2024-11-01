import numpy as np
from flask import Flask, render_template, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room
import random
import time
import threading
import rospy
from std_msgs.msg import String
from qt_robot_interface.srv import *
from qt_gesture_controller.srv import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


selected_character = ''
selected_lodge = ''
porridge_visited = [False]
chair_visited = [False]
bed_visited = [False]

table_visit = [0, 0, 0]
chair_visit =[0, 0, 0]
bed_visit = [0, 0, 0]


global talktext_pub
global speechSay_pub
global emotionShow_pub
global gesturePlay_pub
global audioPlay_pub
global gesturePlay_servc

baby_chair_visit_check = False


@socketio.on('start_talk')
def first_talk_robot_interactive():
    # Display two characters. Becomes the main character of the story
    rospy.sleep(1.0)
    global talktext_pub
    print("first_talk_robot_interactive")
    talktext_pub.publish("Click one of the characters you like")

@socketio.on('first_page')
def second():
    rospy.sleep(1.0)
    # global talktext_pub
    # rospy.sleep(2.0)
    talktext_pub.publish("Once upon a time lived Goldilocks and The Three Bears.")



@socketio.on('girl_lodge')
def third_girl():
    rospy.sleep(1.0)
    # global talktext_pub
    talktext_pub.publish("One day, Goldilocks went for a walk in the forest and found a house. She knocked, and when nobody answered, she decided to go inside.")


@socketio.on('boy_lodge')
def third_boy():
    rospy.sleep(2.0)
    # global talktext_pub
    talktext_pub.publish("One day, Goldilocks went for a walk in the forest and found a house. He knocked, and when nobody answered, he decided to go inside.")

@socketio.on('girl_table')
def table_main(msg):
    rospy.sleep(1.0)
    print("msg: ",msg)
    selected_lodge = msg
    print("porridge_visited: ",porridge_visited[0])

    socketio.emit('checking_visit', "String ", broadcast=True)
    print("msg: ",selected_lodge)

    if(porridge_visited[0]==False and selected_lodge != " "):
        # If this is the first visit on this page, robot speaks to choose one bowl
        rospy.sleep(2.0)
        talktext_pub.publish("At the table, there were three bowls of porridge. Goldilocks was hungry.")

@socketio.on('dad_porridge')
def dad_porridge():
    rospy.sleep(2.0)
    emotionShow_pub.publish("QT/disgusted")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/Ugh")
    porridge_visited[0] = True
    talktext_pub.publish("Goldilocks tasted the porridge from the large bowl. This porridge is too salty")

@socketio.on('mom_porridge')
def mom_porridge():
    rospy.sleep(2.0)
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/No_my")
    porridge_visited[0] = True
    talktext_pub.publish("Goldilocks tasted the porridge from the medium sized bowl. “This porridge is too sweet!")

@socketio.on('baby_porridge')
def baby_porridge():
    rospy.sleep(2.0)
    emotionShow_pub.publish("QT/happy")
    gesturePlay_pub.publish("QT/happy")
    porridge_visited[0] = True
    talktext_pub.publish("Goldilocks tasted the porridge from the small bowl. “This porridge is just right,” Goldilocks said and ate it all up.")


@socketio.on('chair')
def chair_main():
    print("chair connected")
    rospy.sleep(1.0)
    print("chair_visited: ",chair_visited[0])
    print("chair_visit: ",chair_visit)
    socketio.emit('number', chair_visit, broadcast=True)
    if(chair_visited[0]==False):
        print("ddd")
        rospy.sleep(2.0)
        talktext_pub.publish("Goldilocks felt tired, so Goldilocks walked into the living room and saw three chairs.")


@socketio.on('dad_chair')
def dad_chair( ):
    rospy.sleep(2.0)
    print("chair_visit: ", chair_visit)
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/hmm")
    chair_visited[0] = True
    talktext_pub.publish("Goldilocks sat in the large chair to rest her feet. “This chair is too big!")


@socketio.on('mom_chair')
def mom_chair():
    rospy.sleep(2.0)
    print("chair_visit: ", chair_visit)
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/cross_arm")
    chair_visited[0] = True
    talktext_pub.publish("Goldilocks sat in the medium sized chair. This chair is too big, too!")


@socketio.on('baby_chair')
def baby_chair():
    rospy.sleep(2.0)
    global baby_chair_visit_check
    print("chair_visit: ",chair_visit)
    if(baby_chair_visit_check==False):
        # To avoid speak again, after coming back from the 'baby_chair2'
        emotionShow_pub.publish("QT/happy")
        gesturePlay_pub.publish("QT/happy")
        chair_visited[0] = True
        talktext_pub.publish("Goldilocks sat in the small chair. “This chair is just right")
        baby_chair_visit_check = True
    else:
        print("this is revisit from the next page")
        print("Should do nothing")

@socketio.on('baby_chair2')
def baby_chair2():
    rospy.sleep(2.0)
    talktext_pub.publish("Just as Goldilocks settled down into the chair to rest, it broke into pieces!")



@socketio.on('bed')
def bed_main():
    rospy.sleep(1.0)
    print("bed_visited: ",bed_visited[0])
    socketio.emit('number', bed_visit, broadcast=True)
    if(bed_visited[0]==False):
        # If this is the first visit on this page, robot speaks to choose one bowl
        print("bed enter")
        rospy.sleep(2.0)
        talktext_pub.publish("By now, Goldilocks was very tired, Goldilocks went upstairs to the bedroom.")

@socketio.on('dad_bed')
def dad_bed_func( ):
    rospy.sleep(2.0)
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/cross_arm")
    bed_visited[0] = True
    talktext_pub.publish("Goldilocks lay down on the large bed. “This bed is too hard!” ")


@socketio.on('mom_bed')
def mom_bed_func():
    rospy.sleep(2.0)
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/hmm")
    bed_visited[0] = True
    talktext_pub.publish("Goldilocks lay down on the medium sized bed. This bed is too soft!")


@socketio.on('baby_bed')
def baby_bed_func():
    rospy.sleep(2.0)
    gesturePlay_pub.publish("soomin_yawn")
    rospy.sleep(2.5)
    emotionShow_pub.publish("QT/yawn")
    bed_visited[0] = True
    talktext_pub.publish("Goldilocks lay down on the small bed. This bed is just right. Goldilocks curled up and fell asleep.")


# # # # # # # # # # # # Bear  # # # # # # # # # # # # # # # # # # #
@socketio.on('bear_1st')
def bear_1st_func():
    rospy.sleep(2.0)
    talktext_pub.publish("As Goldilocks was sleeping, The Three Bears came home.")
    porridge_visited[0] = False
    chair_visited[0] = False
    bed_visited[0] =False

@socketio.on('bear_2nd')
def bear_2nd_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been eating my porridge, growled Daddy Bear.")
@socketio.on('bear_3rd')
def bear_3rd_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been eating my porridge, said Mummy Bear.")

@socketio.on('bear_4th')
def bear_4th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been eating my porridge and it’s all gone!. Cried Baby Bear")

@socketio.on('bear_5th')
def bear_5th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been sitting in my chair!. Growled Daddy Bear.")

@socketio.on('bear_6th')
def bear_6th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been sitting in my chair!” said Mummy Bear.")

@socketio.on('bear_7th')
def bear_7th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been sitting in my chair and it’s broken!. Cried Baby Bear.")

@socketio.on('bear_8th')
def bear_8th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("When they got upstairs to the bedroom, Daddy Bear growled. Someone’s been sleeping on my bed.")

@socketio.on('bear_9th')
def bear_9th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been sleeping on my bed too, said the Mummy Bear")

@socketio.on('bear_10th')
def bear_10th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been sleeping in my bed, and she’s still there!. Cried Baby Bear.")

@socketio.on('boy_bear_10th')
def boy_bear_10th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Someone’s been sleeping in my bed, and he’s still there!. Cried Baby Bear.")

@socketio.on('bear_11th')
def bear_11th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Just then Goldilocks woke up and saw The Three Bears. Help!. She screamed.")

@socketio.on('boy_bear_11th')
def boy_bear_11th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Just then Goldilocks woke up and saw The Three Bears. Help!. He screamed.")

@socketio.on('bear_12th')
def bear_12th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Goldilocks ran down the stairs and into the forest. And she never went back into the woods again.")


@socketio.on('boy_bear_12th')
def boy_bear_12th_func():
    rospy.sleep(2.0)
    talktext_pub.publish("Goldilocks ran down the stairs and into the forest. And he never went back into the woods again.")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
@socketio.on('boy_table')
def boy_table_main(msg):
    rospy.sleep(1.0)
    print("msg: ",msg)
    selected_lodge = msg
    print("porridge_visited: ",porridge_visited[0])
    socketio.emit('checking_visit', "String ", broadcast=True)
    print("msg: ",selected_lodge)

    if(porridge_visited[0]==False and selected_lodge != " "):
        # If this is the first visit on this page, robot speaks to choose one bowl
        rospy.sleep(2.0)
        talktext_pub.publish("At the table, there were three bowls of porridge. Goldilocks was hungry.")



def interact_main():
    threading.Thread(target=lambda: rospy.init_node('interact',
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

