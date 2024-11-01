import numpy as np
from flask import Flask, render_template, redirect, url_for, session, request
from flask_socketio import SocketIO, emit, join_room
#from flask_cors import CORS
import random
import time
import threading
import rospy
from std_msgs.msg import String
from anytree import Node, RenderTree
from qt_robot_interface.srv import *
from qt_gesture_controller.srv import *
from std_msgs.msg import Float64MultiArray


from emotion_card import *
from object_action_card import *
from emotion_card2 import *
from emotion_card3 import *
from flask_mysqldb import MySQL
import mysql.connector as sql

from interact_story import *
# from dice_rolling import *
path = "/static/images/"

# f = open("instruction_.txt", "w")

table_id = ''
error_record = 0
success_record=0

arr_visit = [False, False, False]
praise_order = [0, 1, 2, 3]
encourage_order = [0, 1, 2]
random.shuffle(praise_order)
random.shuffle(encourage_order)
random_praise = 0
random_encouragement = 0

emotion_game1_success =0
emotion_game2_success =0
emotion_game3_success =0
emotion_game1_failure =0
emotion_game2_failure =0
emotion_game3_failure =0


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

file_name = "test"
app.config['MYSQL_HOST'] = 'http://127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'USERS'

conn =sql.connect(host='localhost',user='root', password='root',database='USERS')

mysql = MySQL(app)

@socketio.on('category_talk')
def first_talk_robot():
    print(arr_visit)
    # rospy.sleep(2.0)
    socketio.emit('number', arr_visit, broadcast=True)
    if arr_visit[0] == False:
        talktext_pub.publish("Let's go to the supermarket!")
        rospy.sleep(3.0)
        # talktext_pub.publish("Touch the correct one on the tablet!")  # Instruction
        arr_visit[0] = True
    elif arr_visit[0] == True and arr_visit[1] == False:
        # audioPlay_pub.publish(" ") #hospital audio
        talktext_pub.publish("Let's go to the hospital")
        rospy.sleep(2.5)
        # talktext_pub.publish("Touch the correct one on the tablet!")  # Instruction
        arr_visit[1] = True
    elif arr_visit[0] == True and arr_visit[1] == True and arr_visit[2] == False:
        talktext_pub.publish("Let's go to the park")  # park
        rospy.sleep(3.0)
        # talktext_pub.publish("Touch the correct one on the tablet!")  # Instruction
        arr_visit[2] = True
    else:
        talktext_pub.publish("All done! Let's go back!")  # park

    print("error_record, success_record: ", error_record, success_record)
    cur = conn.cursor()
    global table_id
    print("table_id: ",table_id)
    query = f"INSERT INTO {table_id} (success, fail) VALUES (%s, %s)"
    cur.execute(query, (success_record, error_record))
    conn.commit()
    cur.close()


@socketio.on('init_after_category')
def init_interaction_robot(msg):
    print("message: ", msg)
    talktext_pub.publish(msg)
    

@socketio.on('first_talk')
def first_talk_robot(msg):
    print("message: ", msg)
    rospy.sleep(1.0)
    talktext_pub.publish(msg)


@socketio.on('giveme_talk')
def giveme_talk_robot(msg):
    print("message: ", msg)
    rospy.sleep(1.5)
    talktext_pub.publish(msg)


@socketio.on('object_list')
def correct_answer(obj):
    print(str(obj))
    global file_name
    with open(file_name,'a+') as f:
        f.write(obj["data"] +" selected " "\n")




@socketio.on('correct')
def correct_answer():
    global random_praise
    global emotionShow_pub
    global gesturePlay_servc
    emotionShow_pub.publish("QT/happy") 
    
    if random_praise == 4:
        random_praise = 0
        random.shuffle(praise_order)  # shuffle again
    if praise_order[random_praise] == 0:
        gesturePlay_servc("QT/happy", 2)
        talktext_pub.publish("Good job!")
        random_praise += 1
        # audioPlay_pub.publish("QT/good_job")
    elif praise_order[random_praise] == 1:
        gesturePlay_servc("QT/happy", 2)
        talktext_pub.publish("Well done!")
        random_praise += 1
        # audioPlay_pub.publish("QT/well_done")
    elif praise_order[random_praise] == 2:
        gesturePlay_servc("QT/emotions/hoora", 2)
        talktext_pub.publish("Amazing!")
        random_praise += 1
        # audioPlay_pub.publish("QT/amazing")
    else:
        gesturePlay_servc("QT/emotions/hoora", 2)
        talktext_pub.publish("Great job!")
        random_praise += 1
        # audioPlay_pub.publish("QT/amazing")

    global success_record
    success_record+=1


@socketio.on('wrong')
def score_handle_from_html():
    global random_encouragement
    global emotionShow_pub
    global gesturePlay_servc
    ref_r = Float64MultiArray()
    ref_l = Float64MultiArray()
    emotionShow_pub.publish("QT/sad") 
    gesturePlay_servc("QT/sad", 1) # it needs to down both hands after performing the gestures
    
    
    #[shoulderPitch, shoulderRoll, elbowRoll]
    ref_r.data = [-85,-65, -20]
    ref_l.data = [88, -71, -23]

    
    
    if random_encouragement == 3:
        random_encouragement = 0
        random.shuffle(encourage_order)  # shuffle again

    if encourage_order[random_encouragement] == 0:
        talktext_pub.publish("Try again!")
        random_encouragement += 1

    elif encourage_order[random_encouragement] == 1:
        talktext_pub.publish("Do it again!")
        random_encouragement += 1

    else:
        talktext_pub.publish("Choose another one!")
        random_encouragement += 1
    right_pub.publish(ref_r)
    left_pub.publish(ref_l)

    global error_record
    error_record +=1



@socketio.on('wrong_repeat')
def speak_repeat(msg):
    emotionShow_pub.publish("QT/sad") 
    rospy.sleep(3.0)
    talktext_pub.publish(str(msg))


@socketio.on('block_page')
def block_page_redirect(msg):
    rospy.sleep(1.0)
    talktext_pub.publish(str(msg))


@socketio.on('next_page')
def block_page_redirect():
    rospy.sleep(3.0)
    talktext_pub.publish("Let's go to the next page!")


@socketio.on('end')
def first_talk_robot():
    # gesturePlay_servc("QT/happy", 2)
    rospy.sleep(1.0)
    talktext_pub.publish("Let's play another game!")


@socketio.on('connect event')
def test_connect(message):
    print(message)


@socketio.on('disconnect')
def test_connect():
    print("disconnected")


@app.route('/')
def login():
    return render_template('login.html')


@socketio.on('login')
def logged_in(message):
    name = message['name']
    session = message["session_no"]
    age = message["age"]
    global f
    global file_name
    file_name = name + "_" + age + "_" + session+".txt"
    f = open(file_name , "a")
    f.write("Name: " + name + "\n")
    f.write("Age: " + age + "\n")
    f.write("Session: " + session + "\n")
    global table_id
    table_id = f"{name}_{age}_{session}"
    # Ensure table ID contains valid SQL table name characters (remove special characters)
    table_id = ''.join(e for e in table_id if e.isalnum() or e == '_')
    cur = conn.cursor()
    # query = "CREATE TABLE IF NOT EXISTS table_id (name  VARCHAR(40), session INT, age INT, success INT, fail INT )"
    query = f"CREATE TABLE IF NOT EXISTS {table_id} (name  VARCHAR(40), session INT, age INT, success INT, fail INT )"

    cur.execute(query)
    conn.commit()

    query = f"INSERT INTO {table_id} (name, session, age) VALUES (%s, %s, %s)"
    cur.execute(query, (name, session , age))
    conn.commit()
    cur.close()
    socketio.emit('redirect', {'url': url_for('main_page')})


@socketio.on('click_main')
def main_menu(message):
    global game
    global f
    global file_name
    global error_record
    global success_record
    game = ""
    with open(file_name,'a+') as f:
        start = time.ctime()
        f.write(message["who"] + "\n")
        f.write("Time: " + time.ctime() + "\n")
    if (message["who"] == 'instructions_game'):
        socketio.emit('redirect', {'url': url_for('taking_instruction')})
    elif (message["who"] == 'emotion_game_1'):
        main()
        game = "emotion_game1"
        socketio.emit('redirect', {'url': url_for('emotion_games_start')})
    elif(message["who"] == 'action_game'):
        main_action()
        game = "action_game"
        socketio.emit('redirect', {'url': url_for('emotion_games_start')})

    elif(message["who"] == 'emotion_game2'):
        game = "emotion_game2"
        main()
        socketio.emit('redirect', {'url': url_for('emotion_games_start')})
    elif(message["who"] == 'emotion_game3'):
        main_emotion_game3()
        game = "emotion_game3"
        socketio.emit('redirect', {'url': url_for('emotion_games_start')})
    elif (message["who"] == 'story'):
        interact_main()
        socketio.emit('redirect', {'url': url_for('start_page_story')})
    elif (message["who"] == 'dice_emotion'):
        dice_main_emotion_young()
        socketio.emit('redirect', {'url': url_for('dice_emotion_young_start')})





@app.route('/main')
def main_page():
    return render_template('main.html')

@socketio.on('client_disconnecting')
def disconnect_details(data):
    global f 
    global file_name
    with open(file_name,'a+') as f:
    # f.open(file_name , "a")
    # print("time.ctime(): ",time.ctime())
        f.write(data['data'] + " closed " + " " + time.ctime() + "\n")
    f.close()
    if(data['data'] == "emotion_game1" or data['data'] == "emotion_game2"):
        exit_main()
    elif(data['data'] == "action_game"):
        exit_main_action()
    elif(data['data'] == "emotion_game3"):
        exit_main_game()

@app.route('/taking_instruction_main')
def taking_instruction():
    return render_template('Taking_Instructions_main.html')


@app.route('/first_page')
def taking_instruction1():
    rospy.sleep(1.0)
    # talktext_pub.publish("I want fruits!")
    return render_template('index_taking_instruction.html')


@app.route('/emotion_games')
def emotion_games_start():
    return render_template('start_game.html')


@app.route('/second_page')
def taking_instruction2():
    rospy.sleep(1.0)
    return render_template('index_taking_instruction_page2.html')


@app.route('/third_page')
def taking_instruction3():
    rospy.sleep(1.0)
    return render_template('index_taking_instruction_page3.html')


@app.route('/hospital_first')
def hospital1():
    rospy.sleep(1.0)
    return render_template('hospital1_instruction.html')


@app.route('/hospital_second')
def hospital2():
    rospy.sleep(1.0)
    return render_template('hospital2_instruction.html')


@app.route('/park_first')
def park1():
    rospy.sleep(1.0)
    return render_template('park1_instruction.html')


@app.route('/park_second')
def park2():
    rospy.sleep(1.0)
    return render_template('park2_instruction.html')


@socketio.on('character_select')
def character_select_func(msg):
    print("msg: ",msg)
    global selected_character
    selected_character = msg
    print('character_select: ', selected_character)

@socketio.on('lodge_select')
def lodge_select_func(msg):
    print("msg: ",msg)
    global selected_lodge
    selected_lodge = msg
    print('lodge_select: ', selected_lodge)

@socketio.on('checking_visit')
def visit_check(visit_chck_data):
    print("visit_check from html")
    print("visit_chck_data: ",visit_chck_data)
    global table_visit

    for i in range(0,len(visit_chck_data)):
        if visit_chck_data[i] ==1:
            table_visit[i] =1
    print("interact_story.table_visit :", table_visit )
    socketio.emit('html_data_recv',table_visit)

@socketio.on('checking_visit_after_click')
def visit_check_click():
    socketio.emit('html_data_recv', table_visit)

@socketio.on('checking_visit_chair')
def visit_check_chair(visit_chck_data):
    global chair_visit

    for i in range(0,len(visit_chck_data)):
        if visit_chck_data[i] ==1:
            chair_visit[i] =1
    socketio.emit('html_data_recv',chair_visit)

@socketio.on('checking_visit_chair_after_click')
def visit_check_chair_click():
    socketio.emit('html_data_recv', chair_visit)


@socketio.on('checking_visit_bed')
def visit_check_bed(visit_chck_data):
    global bed_visit

    for i in range(0,len(visit_chck_data)):
        if visit_chck_data[i] ==1:
            bed_visit[i] =1
    socketio.emit('html_data_recv',bed_visit)

@socketio.on('checking_visit_bed_after_click')
def visit_check_bed_click():
    socketio.emit('html_data_recv', bed_visit)



@app.route('/story_start')
def start_page_story():
    # all checking variables initialized
    global porridge_visited
    global chair_visited
    global bed_visited

    global bed_visit
    global chair_visit
    global table_visit


    porridge_visited[0] = False
    chair_visited[0] = False
    bed_visited[0] = False

    bed_visit = [0, 0, 0]
    chair_visit = [0, 0, 0]
    table_visit = [0, 0, 0]

    first_talk_robot_interactive()
    return render_template('story_character_select.html')

@app.route('/girl/first_page')
def girl_2nd_page():
    second()
    return render_template('1st_girl.html')

@app.route('/boy/first_page')
def boy_2nd_page():
    second()
    return render_template('1st_boy.html')

@app.route('/girl/lodge')
def girl_lodge():
    third_girl()
    return render_template('girl_lodge.html')

@app.route('/boy/lodge')
def boy_lodge():
    third_boy()
    return render_template('boy_lodge.html')
@app.route('/girl/bowl')
def bowl_table():
    table_main(selected_lodge)
    print("table_visit: ",table_visit)
    return render_template('girl_table.html')

@app.route('/boy/bowl')
def boy_bowl_table():
    boy_table_main(selected_lodge)
    return render_template('boy_table.html')

@app.route('/girl/dad_bowl')
def dad_bowl():
    dad_porridge()
    return render_template('dad_bowl_page.html')

@app.route('/girl/mom_bowl')
def mom_bowl():
    mom_porridge()
    return render_template('mom_bowl_page.html')

@app.route('/girl/baby_bowl')
def baby_bowl():
    baby_porridge()
    return render_template('baby_bowl_page.html')

@app.route('/boy/dad_bowl')
def boy_dad_bowl():
    dad_porridge()
    return render_template('/boy/dad_bowl_page.html')

@app.route('/boy/mom_bowl')
def boy_mom_bowl():
    mom_porridge()
    return render_template('/boy/mom_bowl_page.html')

@app.route('/boy/baby_bowl')
def boy_baby_bowl():
    baby_porridge()
    return render_template('/boy/baby_bowl_page.html')


@app.route('/girl/chair')
def chairs():
    chair_main()
    return render_template('chairs.html')

@app.route('/girl/dad_chair')
def dad_chairs():
    dad_chair()
    return render_template('dad_chair_page.html')

@app.route('/girl/mom_chair')
def mom_chairs():
    mom_chair()
    return render_template('mom_chair_page.html')
@app.route('/girl/baby_chair')
def baby_chairs():
    baby_chair()
    print("chair_visit main file: ", chair_visit)
    return render_template('baby_chair_page.html')
@app.route('/girl/baby_chair2')
def baby_chairs2():
    baby_chair2()
    return render_template('baby_chair_page2.html')
@app.route('/boy/chair')
def boy_chairs():
    chair_main()
    return render_template('/boy/chairs.html')

@app.route('/boy/dad_chair')
def boy_dad_chairs():
    dad_chair()
    return render_template('/boy/dad_chair_page.html')

@app.route('/boy/mom_chair')
def boy_mom_chairs():
    chair_main()
    return render_template('/boy/mom_chair_page.html')

@app.route('/boy/baby_chair')
def boy_baby_chairs():
    baby_chair()
    return render_template('/boy/baby_chair_page.html')

@app.route('/boy/baby_chair2')
def boy_baby_chairs2():
    baby_chair2()
    return render_template('/boy/baby_chair_page2.html')
@app.route('/girl/bed')
def beds():
    bed_main()
    return render_template('beds.html')
@app.route('/girl/dad_bed')
def dad_bed():
    dad_bed_func()
    return render_template('dad_bed_page.html')

@app.route('/girl/mom_bed')
def mom_bed():
    mom_bed_func()
    return render_template('mom_bed_page.html')

@app.route('/girl/baby_bed')
def baby_bed():
    baby_bed_func()
    return render_template('baby_bed_page.html')

@app.route('/boy/bed')
def boy_beds():
    bed_main()
    return render_template('/boy/beds.html')

@app.route('/boy/dad_bed')
def boy_dad_bed():
    dad_bed_func()
    return render_template('/boy/dad_bed_page.html')

@app.route('/boy/mom_bed')
def boy_mom_bed():
    mom_bed_func()
    return render_template('/boy/mom_bed_page.html')

@app.route('/boy/baby_bed')
def boy_baby_bed():
    baby_bed_func()
    return render_template('/boy/baby_bed_page.html')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.route('/bear_1st')
def bear_1st():
    bear_1st_func()
    return render_template('bear_1st_page.html')

# @app.route('/girl/bear_2nd')
@app.route('/bear_2nd')
def bear_2nd():
    bear_2nd_func()
    return render_template('bear_2nd_page.html')

# @app.route('/girl/bear_3th')
@app.route('/bear_3rd')
def bear_3th():
    bear_3rd_func()
    return render_template('bear_3th_page.html')

# @app.route('/girl/bear_4th')
@app.route('/bear_4th')
def bear_4th():
    bear_4th_func()
    return render_template('bear_4th_page.html')

# @app.route('/girl/bear_5th')
@app.route('/bear_5th')
def bear_5th():
    bear_5th_func()
    return render_template('bear_5th_page.html')

# @app.route('/girl/bear_6th')
@app.route('/bear_6th')
def bear_6th():
    bear_6th_func()
    return render_template('bear_6th_page.html')

# @app.route('/girl/bear_7th')
@app.route('/bear_7th')
def bear_7th():
    bear_7th_func()
    return render_template('bear_7th_page.html')

# @app.route('/girl/bear_8th')
@app.route('/bear_8th')
def bear_8th():
    bear_8th_func()
    return render_template('bear_8th_page.html')

# @app.route('/girl/bear_9th')
@app.route('/bear_9th')
def bear_9th():
    bear_9th_func()
    global selected_character
    print("selected_character: ",selected_character)
    return render_template('bear_9th_page.html',character =selected_character)

@app.route('/girl/bear_10th')
def bear_10th():
    bear_10th_func()
    return render_template('bear_10th_page.html')
@app.route('/girl/bear_11th')
def bear_11th():
    bear_11th_func()
    return render_template('bear_11th_page.html')
@app.route('/girl/bear_12th')
def bear_12th():
    bear_12th_func()
    if selected_lodge=='lodge1':
        return render_template('bear_12th_page1.html')
    else:
        return render_template('bear_12th_page2.html')

@app.route('/boy/bear_10th')
def boy_bear_10th():
    boy_bear_10th_func()
    return render_template('boy/bear_10th_page.html')
@app.route('/boy/bear_11th')
def boy_bear_11th():
    boy_bear_11th_func()
    return render_template('boy/bear_11th_page.html')
@app.route('/boy/bear_12th')
def boy_bear_12th():
    boy_bear_12th_func()
    if selected_lodge=='lodge1':
        return render_template('boy/bear_12th_page1.html')
    else:
        return render_template('boy/bear_12th_page2.html')
######################################################################################### Dice game with URAs     ############################################################################################

@socketio.on('dice_face_in')
def dice_face_in(digit):
    print("dice_face_in: ",digit)

    if digit==0:
        rospy.sleep(1)
        talktext_pub.publish("Click again")
    else:

        rospy.sleep(1)
        talktext_pub.publish(str(digit))
        rospy.sleep(2)
        talktext_pub.publish("Let's move your piece on the board by " + str(digit))




@socketio.on('dice_face_in_young_emotion')
def dice_face_in_young_emotion(dice_face_str):
    global emotionShow_pub
    global gesturePlay_servc

    rospy.sleep(1)
    talktext_pub.publish(dice_face_str)
    if dice_face_str=='anger':

        gesturePlay_servc("QT/angry", 2)
        rospy.sleep(1)
        emotionShow_pub.publish("QT/angry")

    elif dice_face_str=='happy':
        gesturePlay_servc("QT/happy", 2)
        rospy.sleep(1)
        emotionShow_pub.publish("QT/happy")
    elif dice_face_str=='sad':

        gesturePlay_servc("soomin_sad", 2)
        rospy.sleep(1)
        emotionShow_pub.publish("QT/sad")

    elif dice_face_str=='scared':

        gesturePlay_servc("soomin_sad", 2)
        rospy.sleep(1)
        emotionShow_pub.publish("QT/afraid")

    elif dice_face_str=='surprised':
        emotionShow_pub.publish("QT/surprise")
        rospy.sleep(1)

    else:
        emotionShow_pub.publish("QT/disgusted")
        gesturePlay_servc("QT/sad", 2)

    rospy.sleep(2)






@app.route('/dice_emotion_old_start')
def dice_emotion_old_start():
    talktext_pub.publish("Let's roll the dice")
    return render_template('dice_emotion_young.html')

@app.route('/dice_emotion_young_start')
def dice_emotion_young_start():
    talktext_pub.publish("Let's roll the dice")
    return render_template('dice_emotion_young.html')


######################################################################################### Negin     ############################################################################################
# Emotion game1

def emotion_card(id):
    global talktext_pub
    global speechSay_pub
    global emotionShow_pub
    global gesturePlay_pub
    gesturePlay_servc("QT/neutral",2)
    if id == 0:
        rospy.sleep(1.0)
        talktext_pub.publish("angry!")

        rospy.sleep(2.0)
        gesturePlay_pub.publish("/QT/emotions/angry")
        rospy.sleep(1.0)
        emotionShow_pub.publish("QT/angry")
        # r1 = random.randint(0,len(angry)-1)
        # talktext_pub.publish(angry[r1]) 
    elif id == 1: 
        rospy.sleep(1.0)
        talktext_pub.publish("happy!")
        rospy.sleep(1.0)
        emotionShow_pub.publish("QT/happy")
        rospy.sleep(5.0)
        gesturePlay_pub.publish("/QT/emotions/happy")    
        # r2 = random.randint(0,len(happy)-1)
        # talktext_pub.publish(happy[r2]) 
    elif id == 2:
        rospy.sleep(1.0)
        talktext_pub.publish("excited!")
        rospy.sleep(1.0)
        emotionShow_pub.publish("QT/happy_blinking")
        rospy.sleep(5.0)
        gesturePlay_pub.publish("/QT/emotions/hoora")
        # r3 = random.randint(0,len(excited)-1)
        # talktext_pub.publish(excited[r3]) 
    elif id == 3:
        rospy.sleep(1.0)
        talktext_pub.publish("sad!")
        rospy.sleep(1.0)
        emotionShow_pub.publish("QT/sad") 
        rospy.sleep(5.0)
        gesturePlay_pub.publish("/QT/emotions/sad")        
        # r4 = random.randint(0,len(sad)-1)
        # talktext_pub.publish(sad[r4])      
    elif id == 4:
        rospy.sleep(1.0)
        talktext_pub.publish("scared!")
        rospy.sleep(1.0)
        emotionShow_pub.publish("QT/afraid")
        rospy.sleep(5.0)
        gesturePlay_pub.publish("/QT/emotions/afraid")        
        # r5 = random.randint(0,len(scared)-1)
        # talktext_pub.publish(scared[r5])
    elif id == 5:
        rospy.sleep(1.0)
        talktext_pub.publish("shy!")
        rospy.sleep(1.0)
        emotionShow_pub.publish("QT/shy")
        rospy.sleep(5.0)
        gesturePlay_pub.publish("/QT/emotions/shy")
        # r6 = random.randint(0,len(shy)-1)
        # talktext_pub.publish(shy[r6]) 
    if (id < 6 and id > -1):
        rospy.sleep(8)
        talktext_pub.publish("Look at the tablet, which one is " + " " + emotion_dictionary[id]) 
        


emotion_dictionary= {0: "angry", 1: "happy" , 2: "excited", 3: "sad", 4: "scared", 5: "shy"}

def object_card(id):
    talktext_pub.publish(action)
    rospy.sleep(4)
    talktext_pub.publish("Look at the tablet, click on the picture") 

@app.route('/request', methods=['POST'])
def request_callback():
    global game
    global selected
    if (game == "emotion_game1"):
        id = request.form['emotion']
        print("ID: "+id)
        data = emotion_dictionary[int(id)]
        emotion = list(emotions.keys())[list(emotions.values()).index(data)]
        if selected == 0 and int(id) < 7:
            emotion_card(int(id))
            socketio.emit('update image', {'path': random_image_selector(emotion)}, broadcast=True)
    elif (game == "emotion_game2"):
        # data = request.form['emotion']
        # id = list(emotions.keys())[list(emotions.values()).index(data)]
        id = request.form['emotion']
        data = emotion_dictionary[int(id)]
        emotion = list(emotions.keys())[list(emotions.values()).index(data)]        
        if selected == 0: 
            emotion_card(int(id))       
            socketio.emit('update image', {'path': random_image(emotion)}, broadcast=True)
    elif (game == "action_game"):
        global action
        action = request.form['action']
        global speech_flag
        if (not speech_flag):
            socketio.emit('update image', {'path': [path + "/action_cards/" + action + ".png"]}, broadcast=True)
            object_card(action)
    return "pass"

emotions = {0: "happy", 1: "angry", 2: "scared", 3: "excited", 4: "shy", 5: "sad"}



happy = {'ice': 'Having ice cream makes me feel happy!', 'smile': 'when I am happy, I smile!',
         'energy': 'When I am happy, I feel like I have a lot of energy!',
         'jump': 'When I am happy, I want to jump for joy!'}
sad = {'sad': 'When I am sad, my smile disappears', 'toy': 'My favorite toy is broken, it makes me feel sad!',
       'friend_sad': 'My friend is sad, it makes me feel sad too!'}
angry = {'scream': 'When I feel angry, I want to scream and yell!'}

shy ={'shy': 'When I feel Shy, I get red in my face'}


excited= {'travel':'Travelling with my family, makes me feel excited'}

scared = {'scared': 'When I feel scared, my legs shake'}



def random_image_selector(id):
    l = []
    x = id
    y = 5 - x
    print(emotions[x])
    l.append(path + "emotions/" + emotions[x] + ".jpg")
    l.append(path + "emotions/" + emotions[y] + ".jpg")
    return l

def random_image(id):
    global var
    if id == 0:
        i = random.randint(0, len(happy) - 1)
        em = list(happy.keys())[i]
        var = happy[em]
    elif id == 1:
        i = random.randint(0, len(angry) - 1)
        em = list(angry.keys())[i]
        var = angry[em]
    elif id == 2:
        i = random.randint(0, len(scared) - 1)
        em = list(scared.keys())[i]
        var = scared[em]
    elif id == 3:
        i = random.randint(0, len(excited) - 1)
        em = list(excited.keys())[i]
        var = excited[em]
    elif id == 4:
        i = random.randint(0, len(shy) - 1)
        em = list(shy.keys())[i]
        var = shy[em]
    elif id == 5:
        i = random.randint(0, len(sad) - 1)
        em = list(sad.keys())[i]
        var = sad[em]
    l = []
    l.append(path + "emotion_game_2/" + em + "1.png")
    l.append(path + "emotion_game_2/" + em + "2.png")
    print("list is :", l)
    return l


@socketio.on('start game')
def start_game(message):
    global selected
    global speech_flag
    global game
    selected = 0
    speech_flag = False
    if (message['who'] == 'start_game'):
        socketio.emit('redirect', {'url': url_for('first_view')})
        if(game == "emotion_game1" or game == "emotion_game2"):
            talktext_pub.publish("Let's play a game, show me an emotion card!")
        elif(game == "emotion_game3"):
            talktext_pub.publish("Let's play a game, show me two emotion cards")
        elif(game == "action_game"):
            talktext_pub.publish("Let's play a game, show me an action card!")
        rospy.sleep(1)



@socketio.on('selected')
def image_selected(message):
    global game
    global selected

    global emotion_game1_success, emotion_game2_success, emotion_game3_success
    global emotion_game1_failure, emotion_game2_failure, emotion_game3_failure
    if(game == "emotion_game1"):
        if(selected == 0):
            if(message['who'] == "img00"):
                socketio.emit('highlight',{},  broadcast = True)
                speechSay_pub.publish("Good job!")
                selected = 1
                rospy.sleep(2)
                talktext_pub.publish("You can click next.")

                emotion_game1_success+=1
            else:
                speechSay_pub.publish("Please try again!")
                emotion_game1_failure += 1
    elif(game == "emotion_game2"):
        global var
        if(selected == 0):
            if(message['who'] == "img00"):
                socketio.emit('highlight',{},  broadcast = True)
                speechSay_pub.publish(var)
                rospy.sleep(1)
                talktext_pub.publish("You can click next.")
                selected = 1
                emotion_game2_success+=1
            else:
                speechSay_pub.publish("Please try again!")
                emotion_game2_failure+=1
    elif(game == "action_game"):
        global speech_flag
        if not speech_flag:
            speech_flag = True
            speechSay_pub.publish(action)
            rospy.sleep(1)
            talktext_pub.publish("You can click next.")   
    #rospy.sleep(1)

@socketio.on('next button')
def next_button(message):
    global game
    global selected
    global speech_flag
    if(game == "emotion_game1" or game  == "emotion_game2"):
        rospy.sleep(2)
        talktext_pub.publish("Show me another emotion card!")
        rospy.sleep(1.5)
        if(selected == 1):
            selected = 0 
            socketio.emit('update image', {'path': [path + "emotions/ask.jpg" , path + "emotions/ask.jpg"]}, broadcast=True)
    elif(game == "action_game"):
        rospy.sleep(2)
        talktext_pub.publish("Show me another action card!")
        global speech_flag
        if(speech_flag == True):
            speech_flag = False 
            socketio.emit('update image', {'path': [path + "emotions/ask.jpg"]}, broadcast=True)

@app.route('/first_view')
def first_view():
    # # time.sleep(10)
    # print("game")
    # return render_template('emotion_game1.html')
    global game
    if(game == "emotion_game1"):
        return render_template('emotion_game1.html')
    elif(game == "emotion_game2"):
        return render_template('emotion_game1.html')
    elif(game == "action_game"):
        return render_template('action_game.html')
    elif(game == "emotion_game3"):
        return render_template('emotion_game3.html')



######################################################################################### Main ############################################################################################

if __name__ == '__main__':
    threading.Thread(target=lambda: rospy.init_node('app', disable_signals=True)).start()  # it helps to start the rospy and ends terminal
    speechSay_pub = rospy.Publisher('/qt_robot/speech/say', String, queue_size=10)
    talktext_pub = rospy.Publisher('/qt_robot/behavior/talkText', String, queue_size=10)
    gesturePlay_pub = rospy.Publisher('/qt_robot/gesture/play', String, queue_size=10)
    emotionShow_pub = rospy.Publisher('/qt_robot/emotion/show', String, queue_size=10)
    audioPlay_pub = rospy.Publisher('/qt_robot/audio/play', String, queue_size=10)
    
    gesturePlay_servc = rospy.ServiceProxy('/qt_robot/gesture/play', gesture_play)
    rospy.wait_for_service('/qt_robot/gesture/play')
    
    right_pub = rospy.Publisher('/qt_robot/right_arm_position/command', Float64MultiArray, queue_size=1)
    left_pub = rospy.Publisher('/qt_robot/left_arm_position/command', Float64MultiArray, queue_size=1)   
    global f
    time_start = time.ctime()

    socketio.run(app, host='0.0.0.0', debug=True)  # connect to 192.168.100.2:5000 in web
    end = time.ctime()

    



