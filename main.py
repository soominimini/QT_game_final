import os
from datetime import datetime
from http.cookiejar import debug
from symbol import continue_stmt

from flask import Flask, render_template, redirect, url_for, session, request, send_from_directory, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room
# from flask_cors import CORS
import random
import re
import time
import threading
import rospy
from std_msgs.msg import String
# from anytree import Node, RenderTree
from qt_robot_interface.srv import *
from qt_gesture_controller.srv import *
from std_msgs.msg import Float64MultiArray

from emotion_card import *
from object_action_card import *
from emotion_card2 import *
from emotion_card3 import *
from flask_mysqldb import MySQL
import mysql.connector as sql

# from interact_story import *

# from dice_rolling import *
path = "/static/images/"

# f = open("instruction_.txt", "w")


is_redirecting = False
sub = None
state = 0
em = None

table_id = ''
error_record = 0
success_record = 0

selected_character = ''
selected_lodge = ''
porridge_visited = [False]
chair_visited = [False]
bed_visited = [False]

baby_chair_visit_check = False
table_visit = [0, 0, 0]
chair_visit = [0, 0, 0]
bed_visit = [0, 0, 0]

show_text = False
arr_visit = [False, False, False]
praise_order = [0, 1, 2, 3]
encourage_order = [0, 1, 2]
random.shuffle(praise_order)
random.shuffle(encourage_order)
random_praise = 0
random_encouragement = 0

emotion_game1_success = 0
emotion_game2_success = 0
emotion_game3_success = 0
emotion_game1_failure = 0
emotion_game2_failure = 0
emotion_game3_failure = 0

head_idle = []

Idle_gestures = ["both_arms", "right_arm", "left_arm", "natural_arms_wide", "head_arm_natural"]

idle_arm_gestures = ["idle_arms_up_1"]
emotion_dictionary = {0: "angry", 1: "happy", 2: "excited", 3: "sad", 4: "scared", 5: "shy"}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

file_name = "test"
app.config['MYSQL_HOST'] = 'http://127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'USERS'

conn = sql.connect(host='localhost', user='root', password='root', database='USERS')

mysql = MySQL(app)

stop_triggered_flag = False

speech_stop_event = threading.Event()  # Global stop signal for speech
emotion_stop_event = threading.Event()
gesture_stop_event = threading.Event()
audio_stop_event = threading.Event()

global_sentence = ''


def neutralize():
    gesturePlay_servc("QT/neutral", 0.5)
# "idle_left_arm_and_head", "idle_right_arm_and_head",
def get_short_idle_gesture():
    gestures = ["idle_arms_up_1", "idle_arms_1", "idle_arms_2", "head_arm_natural","natural_arms_wide","both_arms", "idle_test_1", "idle_test_arm"]
    return random.choice(gestures)

def text_split(text, num_chars=65):
    # Define a pattern for punctuation marks or commas
    pattern = r'([.!?.,;])'

    text = text.strip()

    # Find all positions where a punctuation mark occurs
    split_positions = [m.start() for m in re.finditer(pattern, text)]

    chunks = []
    start = 0

    for pos in split_positions:
        # If the chunk length from the last split point is greater than 100, we split
        if pos - start >= num_chars:
            chunks.append(text[start:pos+1].strip())
            start = pos + 1  # Update the starting position for the next chunk

    # Add the final chunk if there are any leftover characters
    if start < len(text):
        chunks.append(text[start:].strip())

    return chunks

@socketio.on('stop_trigger_force')
def handle_speech_stop_force(data):
    global stop_triggered_flag
    stop_triggered_flag = True
    print("Speech stop event triggered.")


def execute_jumping_jacks():
    global stop_triggered_flag
    for i in range(1, 11):
        if stop_triggered_flag:
            print("Stop triggered during jumping jacks!")
            break
        else:
            print("Doing jumping jack", i)
            time.sleep(2)  # Simulate the delay for each jumping jack

        rospy.sleep(1)
        talktext_pub.publish(str(i))
        handle_gesture_play("jumping_soomin", 2)
    stop_triggered_flag = False


@socketio.on('speech_stop')
def handle_speech_stop(data):
    speech_stop_event.set()  # Signal to stop speech
    emotion_stop_event.set()
    gesture_stop_event.set()
    audio_stop_event.set()
    speechStop_servc()  # Call the speech stop service
    gestureStop_servc()
    emotionStop_servc()
    audioPlay_servc()
    talktext_pub.publish("all done")
    neutralize()

    print("Speech stop event triggered.")


@socketio.on('speech_say')
def handle_speech_say(data):
    def say_speech():
        speech_stop_event.clear()  # Reset stop signal before starting speech
        # speechSay_pub.publish(data)  # Publish speech
        # speechSay_servc(data)
        talktext_pub.publish(data)

    # Run speech processing in a separate thread
    threading.Thread(target=say_speech).start()
    print("Speech say event received:", data)




@socketio.on('emotion_play')
def handle_emotion_play(data):
    def play_emotion():
        emotion_stop_event.clear()  # Reset stop signal before starting speech
        emotionShow_pub.publish(data)  # Publish speech

    # Run speech processing in a separate thread
    threading.Thread(target=play_emotion).start()
    print("Emotion play event received:", data)


@socketio.on('gesture_play')
def handle_gesture_play(data, speed):
    def play_gesture():
        gesture_stop_event.clear()  # Reset stop signal before starting speech
        gesturePlay_servc(data, speed)

    # Run speech processing in a separate thread
    threading.Thread(target=play_gesture).start()
    print("Gesture play event received:", data)


@socketio.on('gesture_play_pub')
def handle_gesture_play_pub(data):
    gesturePlay_pub.publish(data)
    print("Gesture play event received:", data)


@socketio.on('audio_play')
def handle_audio_play(data):
    def play_audio():
        audio_stop_event.clear()  # Reset stop signal before starting speech
        audioPlay_pub.publish(data)

    # Run speech processing in a separate thread
    threading.Thread(target=play_audio).start()
    print("Audio play event received:", data)


@socketio.on('repeat_speech')
def handle_repeat_speach(data):
    if data == '':
        global global_sentence
        data = global_sentence

    print("repeat_speech: ", data)

    def say_speech_repeat():
        speech_stop_event.clear()  # Reset stop signal before starting speech
        # speechSay_pub.publish(data)  # Publish speech
        # speechSay_servc(data)
        # talktext_pub.publish(data)

        behaviorTalk_servc(data)
        # Run speech processing in a separate thread

    threading.Thread(target=say_speech_repeat).start()
    print("Speech say event received:", data)

#     #     #     #     #     #     #     #     #     #     #     # #     #     #    STOP functions  #     #     #     #     #     #     #     #     #     #     #     #     #     #
@socketio.on('story_text')
def handle_story_speech(data):
    def story_speech():
        speech_stop_event.clear()  # Reset stop signal before starting speech
        # speechSay_pub.publish(data)  # Publish speech
        behaviorTalk_servc(data)

    # Run speech processing in a separate thread
    threading.Thread(target=story_speech).start()
    print("Speech say event received:", data)


@socketio.on('category_talk')
def first_talk_robot():
    print(arr_visit)
    global global_sentence
    rospy.sleep(1.0)

    # List of sentences to choose from
    sentences = [
        "Where do you wanna go?",
        "Where do you want to go?",
        "Where do you feel like going?",
        "Where shall we go?",
        "What place do you wanna go to?"
    ]
    # Randomly select a sentence
    selected_sentence = random.choice(sentences)
    # Say the selected sentence
    talktext_pub.publish(selected_sentence)

    gesturePlay_pub.publish(get_short_idle_gesture())

    # Update the global sentence
    global_sentence = selected_sentence


@socketio.on('init_after_category')
def init_interaction_robot(msg):
    print("message: ", msg)
    rospy.sleep(0.5)
    talktext_pub.publish(msg)

@socketio.on('first_talk')
def first_talk_robot(msg):
    print("message: ", msg)
    rospy.sleep(1.0)
    handle_speech_say(msg)
    # talktext_pub.publish(msg)

    gesturePlay_pub.publish(get_short_idle_gesture())


@socketio.on('giveme_talk')
def giveme_talk_robot(msg, time_sleep):
    print("message: ", msg)
    # handle_speech_say(msg)
    rospy.sleep(time_sleep)
    talktext_pub.publish(msg)

    rospy.sleep(2.5)

@socketio.on('object_list')
def correct_answer(obj):
    print(str(obj))
    global file_name
    with open(file_name, 'a+') as f:
        f.write(obj["data"] + " selected " "\n")


@socketio.on('simple_correct')
def simple_correct_answer_res():
    rospy.sleep(0.5)
    talktext_pub.publish("That's correct")


@socketio.on('simple_wrong')
def simple_wrong_answer_res():
    rospy.sleep(0.5)
    talktext_pub.publish("That's not correct")


@socketio.on('correct')
def correct_answer():
    global random_praise
    global emotionShow_pub
    global gesturePlay_servc
    # emotionShow_pub.publish("QT/happy")

    rospy.sleep(1)
    if random_praise == 4:
        random_praise = 0
        random.shuffle(praise_order)  # shuffle again
    if praise_order[random_praise] == 0:
        handle_speech_say("You’re doing so well!")
        rospy.sleep(1)
        handle_emotion_play("QT/happy")
        handle_gesture_play("QT/happy", 2)
        # gesturePlay_servc("QT/happy", 2)
        # talktext_pub.publish("Good job!")
        random_praise += 1
        # audioPlay_pub.publish("QT/good_job")
    elif praise_order[random_praise] == 1:

        handle_speech_say("Well done!")
        rospy.sleep(2)
        handle_emotion_play("QT/happy")
        handle_gesture_play("QT/happy", 2)
        # gesturePlay_servc("QT/happy", 2)
        # talktext_pub.publish("Well done!")
        random_praise += 1
        # audioPlay_pub.publish("QT/well_done")
    elif praise_order[random_praise] == 2:

        handle_speech_say("Amazing!")
        rospy.sleep(1.5)
        handle_emotion_play("QT/happy")
        handle_gesture_play("QT/emotions/hoora", 2)
        # gesturePlay_servc("QT/emotions/hoora", 2)
        # talktext_pub.publish("Amazing!")
        random_praise += 1
        # audioPlay_pub.publish("QT/amazing")
    else:
        handle_speech_say("Great job!")
        rospy.sleep(1)
        handle_emotion_play("QT/happy")
        handle_gesture_play("QT/emotions/hoora", 2)
        # gesturePlay_servc("QT/emotions/hoora", 2)
        # talktext_pub.publish("Great job!")
        random_praise += 1
        # audioPlay_pub.publish("QT/amazing")

    rospy.sleep(1)
    global success_record
    success_record += 1


@socketio.on('wrong')
def score_handle_from_html():
    global random_encouragement
    global emotionShow_pub
    global gesturePlay_servc
    ref_r = Float64MultiArray()
    ref_l = Float64MultiArray()

    # handle_emotion_play("QT/sad")
    emotionShow_pub.publish("QT/sad")
    gesturePlay_pub.publish("QT/sad")
    speechSay_pub.publish("That's not correct!")

    global error_record
    error_record += 1


@socketio.on('wrong_repeat')
def speak_repeat(msg):
    # emotionShow_pub.publish("QT/sad")
    # handle_emotion_play("QT/sad")
    rospy.sleep(3.0)
    # talktext_pub.publish(str(msg))
    handle_speech_say(str(msg))



@socketio.on('block_page')
def block_page_redirect(msg):
    rospy.sleep(1.0)
    # talktext_pub.publish(str(msg))
    handle_speech_say(str(msg))


@socketio.on('next_page')
def block_page_redirect():
    rospy.sleep(2.0)
    # talktext_pub.publish("Let's go to the next page!")
    handle_speech_say("Let's go to the next page!")


@socketio.on('end')
def first_talk_robot():
    # gesturePlay_servc("QT/happy", 2)
    rospy.sleep(1.0)
    # talktext_pub.publish("Let's play another game!")
    handle_speech_say("Let's play another game!")


@socketio.on('connect event')
def test_connect(message):
    print(message)


@socketio.on('disconnect')
def test_connect():
    print("disconnected")


@socketio.on('reload_page')
def reload():
    print("page reload in main")


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/user_confirm')
def user_confirm_func():
    global name
    return render_template('user_confirm.html', username=name)


@socketio.on('login')
def logged_in(message):
    global name
    name = message['name']
    global f
    global file_name

    # Directory where files will be saved
    save_directory = "user_files"
    os.makedirs(save_directory, exist_ok=True)  # Ensure the directory exists

    # Get today's date in YYYY-MM-DD format
    today_date = datetime.now().strftime("%Y-%m-%d")
    base_file_name = f"{name}_"

    # Search for the most recent file created today
    recent_file = None
    for file in sorted(os.listdir(save_directory), reverse=True):
        if file.startswith(base_file_name) and file.endswith(".txt"):
            file_path = os.path.join(save_directory, file)
            file_date = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d")
            if file_date == today_date:  # Check if file was created today
                recent_file = file_path
                break

    # Use the recent file if found; otherwise, create a new file
    if recent_file:
        file_name = recent_file
        print(f"Appending to existing file: {file_name}")
    else:
        # Create a new file with an incremented counter
        counter = 0
        file_name = os.path.join(save_directory, f"{base_file_name}{counter}.txt")
        while os.path.exists(file_name):
            counter += 1
            file_name = os.path.join(save_directory, f"{base_file_name}{counter}.txt")
        print(f"Creating new file: {file_name}")

    # Open file in append mode and write user information
    with open(file_name, "a") as f:
        f.write(f"Name: {name}\n")

    print(f"File saved as: {file_name}")

    # Redirect to the main page
    socketio.emit('redirect', {'url': url_for('main_page')})


@socketio.on('user_confirming')
def user_confirming_func(message):
    global name
    name = message['name']

    # Redirect to the main page
    # socketio.emit('redirect', {'url': url_for('main_page')})


@socketio.on('click_main')
def main_menu(message):
    global is_redirecting, current_game

    global game
    global f
    global file_name
    global error_record
    global success_record
    game = ""
    with open(file_name, 'a+') as f:
        start = time.ctime()
        f.write(message["who"] + "\n")
        f.write("Time: " + time.ctime() + "\n")

        # Prevent multiple redirects
    current_game = game

    print(f"Received click for game: {message['who']}")

    if (message["who"] == 'instructions_game'):
        socketio.emit('redirect', {'url': url_for('taking_instruction')})
    elif (message["who"] == 'instructions_game_young'):
        socketio.emit('redirect', {'url': url_for('taking_instruction_young')})
    elif (message["who"] == 'emotion_game_1'):  # first emotion game for young age
        print("test emotion card file")
        main()
        game = "emotion_game1"
        socketio.emit('redirect', {'url': url_for('emotion_games_start')})

    elif (message["who"] == 'action_game'):  # young age
        main_action()
        game = "action_game"
        socketio.emit('redirect', {'url': url_for('emotion_games_start')})

    elif (message["who"] == 'dice_action_young'):
        socketio.emit('redirect', {'url': url_for('dice_action_young_start')})

    elif (message["who"] == 'emotion_game2'):  # second emotion game for old age
        game = "emotion_game2"
        main()
        socketio.emit('redirect', {'url': url_for('emotion_games_start_2')})
    elif (message["who"] == 'emotion_game3'):
        main_emotion_game3()
        game = "emotion_game3"
        socketio.emit('redirect', {'url': url_for('emotion_games_start')})
    elif (message["who"] == 'story_old_client'):
        socketio.emit('redirect', {'url': url_for('story_old_main')}, room=request.sid)
    elif (message["who"] == 'goldilocks'):
        # interact_main()
        # first_talk_robot_interactive()
        print("here interact")
        socketio.emit('redirect', {'url': url_for('start_page_story')})

    elif (message["who"] == 'red_riding'):
        socketio.emit('redirect', {'url': url_for('red_riding_start')})

    elif (message["who"] == 'dice_emotion_young'):
        # dice_main_emotion_young()
        socketio.emit('redirect', {'url': url_for('dice_emotion_young_start')})

    elif (message["who"] == 'dice_emotion_old'):
        socketio.emit('redirect', {'url': url_for('dice_emotion_old_start')})
    elif (message["who"] == 'dice_5w1h'):
        socketio.emit('redirect', {'url': url_for('dice_5w1h')}, room=request.sid)
    elif (message["who"] == 'dice_5w1h_1'):
        print("here dice_5w1h_1")
        socketio.emit('redirect', {'url': url_for('dice_5w1h_1')})
    elif (message["who"] == 'dice_5w1h_2'):
        socketio.emit('redirect', {'url': url_for('dice_5w1h_2')})
    elif (message["who"] == 'dice_board'):
        socketio.emit('redirect', {'url': url_for('dice_board')})

    elif (message["who"] == 'break'):
        socketio.emit('redirect', {'url': url_for('break_fucn')})
    elif (message["who"] == 'at_talks'):
        socketio.emit('redirect', {'url': url_for('at_talks_func')})
    elif (message["who"] == 'story_young_client'):
        socketio.emit('redirect', {'url': url_for('story_young_main')})
    elif (message["who"] == 'brown_bear'):
        socketio.emit('redirect', {'url': url_for('story_young')})
    elif (message["who"] == 'goodnight'):
        socketio.emit('redirect', {'url': url_for('story_young_moon')})
    elif (message["who"] == 'yes_no_young'):
        socketio.emit('redirect', {'url': url_for('yes_no_young')})
    elif (message["who"] == 'yes_no_old'):
        socketio.emit('redirect', {'url': url_for('yes_no_old')})
    elif (message["who"] == 'inference_old'):
        socketio.emit('redirect', {'url': url_for('inference_fucn')})

@app.route('/main')
def main_page():
    # gesturePlay_servc("head_natural", 1.5)
    # gesturePlay_pub.publish("head_natural")
    # gesturePlay_pub.publish("natural_arms_wide")

    return render_template('main.html')


@socketio.on('client_disconnecting')
def disconnect_details(data):
    global f
    global file_name
    global is_redirecting, current_game

    # Reset the flag on disconnect
    is_redirecting = False
    current_game = None
    print("closing pages")
    with open(file_name, 'a+') as f:
        # f.open(file_name , "a")
        # print("time.ctime(): ",time.ctime())
        f.write(data['data'] + " closed " + " " + time.ctime() + "\n")
    f.close()
    if (data['data'] == "emotion_game1" or data['data'] == "emotion_game2"):
        exit_main()
    elif (data['data'] == "action_game"):
        exit_main_action()
    elif (data['data'] == "emotion_game3"):
        exit_main_game()


@app.route('/taking_instruction_main')
def taking_instruction():
    global arr_visit  # Assuming arr_visit is a global variable
    rand_var = random.randint(0, 5)
    # gesturePlay_servc(Idle_gestures[rand_var], 1.5)
    return render_template('Taking_Instructions_main.html', arr_visit=arr_visit)


@app.route('/taking_instruction_main_young')
def taking_instruction_young():
    print("taking_instruction_young")
    global arr_visit  # Assuming arr_visit is a global variable
    rand_var = random.randint(0, 5)
    # gesturePlay_servc(Idle_gestures[rand_var], 1.5)
    return render_template('/instruction_young/Taking_Instructions_main.html', arr_visit=arr_visit)


@app.route('/first_page')
def taking_instruction1():
    rospy.sleep(1.0)
    # rand_var = random.randint(0, 4)
    # gesturePlay_servc(Idle_gestures[rand_var], 1.5)
    # talktext_pub.publish("I want fruits!")
    return render_template('index_taking_instruction.html')


@app.route('/supermarket_firstpage_young')
def taking_instruction1_young():
    rospy.sleep(1.0)
    # rand_var = random.randint(0, 4)
    # gesturePlay_servc(Idle_gestures[rand_var], 1.5)
    # talktext_pub.publish("I want fruits!")
    return render_template('/instruction_young/index_taking_instruction.html')


@app.route('/emotion_games')
def emotion_games_start():
    rand_var = random.randint(0, 4)
    # gesturePlay_servc(Idle_gestures[rand_var], 1.5)
    gesturePlay_pub.publish(Idle_gestures[rand_var])
    return render_template('start_game.html')


@app.route('/emotion_games2')
def emotion_games_start_2():
    rand_var = random.randint(0, 4)
    # gesturePlay_servc(Idle_gestures[rand_var], 1.5)
    gesturePlay_pub.publish(Idle_gestures[rand_var])
    return render_template('start_game2.html')


@app.route('/second_page')
def taking_instruction2():
    rospy.sleep(1.5)
    return render_template('index_taking_instruction_page2.html')


@app.route('/supermarket_secondpage_young')
def taking_instruction2_young():
    rospy.sleep(1.5)
    return render_template('/instruction_young/index_taking_instruction_page2.html')


@app.route('/third_page')
def taking_instruction3():
    rospy.sleep(1.0)
    return render_template('index_taking_instruction_page3.html')


@app.route('/supermarket_thirdpage_young')
def taking_instruction3_young():
    rospy.sleep(1.0)
    return render_template('/instruction_young/index_taking_instruction_page3.html')


@app.route('/hospital_first')
def hospital1():
    rospy.sleep(1.0)
    return render_template('hospital1_instruction.html')


@app.route('/hospital_first_young')
def hospital1_young():
    rospy.sleep(1.0)
    return render_template('/instruction_young/hospital1_instruction.html')


@app.route('/hospital_second')
def hospital2():
    rospy.sleep(1.0)
    return render_template('hospital2_instruction.html')


@app.route('/hospital_second_young')
def hospital2_young():
    rospy.sleep(1.0)
    return render_template('/instruction_young/hospital2_instruction.html')


@app.route('/hospital_third')
def hospital3():
    rospy.sleep(1.0)
    return render_template('hospital3_instruction.html')


@app.route('/hospital_third_young')
def hospital3_young():
    rospy.sleep(1.0)
    return render_template('/instruction_young/hospital3_instruction.html')


@app.route('/park_first')
def park1():
    rospy.sleep(1.0)
    return render_template('park1_instruction.html')


@app.route('/park_first_young')
def park1_young():
    rospy.sleep(1.0)
    return render_template('/instruction_young/park1_instruction.html')


@app.route('/park_second')
def park2():
    rospy.sleep(1.0)
    return render_template('park2_instruction.html')


@app.route('/park_second_young')
def park2_young():
    rospy.sleep(1.0)
    return render_template('/instruction_young/park2_instruction.html')


@app.route('/park_third')
def park3():
    rospy.sleep(1.0)
    return render_template('park3_instruction.html')


@app.route('/park_third_young')
def park3_young():
    rospy.sleep(1.0)
    return render_template('/instruction_young/park3_instruction.html')


@socketio.on('character_select')
def character_select_func(msg):
    print("msg: ", msg)
    global selected_character
    global show_text

    selected_character = msg
    show_text = msg['showText']

    print(f"Character selected: {selected_character}, Show text: {show_text}")


@socketio.on('lodge_select')
def lodge_select_func(msg):
    print("msg: ", msg)
    global selected_lodge
    selected_lodge = msg
    print('lodge_select: ', selected_lodge)


@socketio.on('checking_visit')
def visit_check(visit_chck_data):
    print("visit_check from html")
    print("visit_chck_data: ", visit_chck_data)
    global table_visit

    for i in range(0, len(visit_chck_data)):
        if visit_chck_data[i] == 1:
            table_visit[i] = 1
    print("interact_story.table_visit :", table_visit)
    socketio.emit('html_data_recv', table_visit)


@socketio.on('checking_visit_after_click')
def visit_check_click():
    socketio.emit('html_data_recv', table_visit)


@socketio.on('checking_visit_chair')
def visit_check_chair(visit_chck_data):
    global chair_visit

    for i in range(0, len(visit_chck_data)):
        if visit_chck_data[i] == 1:
            chair_visit[i] = 1
    socketio.emit('html_data_recv', chair_visit)


@socketio.on('checking_visit_chair_after_click')
def visit_check_chair_click():
    socketio.emit('html_data_recv', chair_visit)


@socketio.on('checking_visit_bed')
def visit_check_bed(visit_chck_data):
    global bed_visit

    for i in range(0, len(visit_chck_data)):
        if visit_chck_data[i] == 1:
            bed_visit[i] = 1
    socketio.emit('html_data_recv', bed_visit)


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

    print("func start_page_story")
    first_talk_robot_interactive()
    return render_template('story_character_select.html')


@app.route('/girl/first_page')
def girl_2nd_page():
    # second()
    return render_template('1st_girl.html', show_text=show_text)


@app.route('/girl/lodge')
def girl_lodge():
    # third_girl()
    return render_template('girl_lodge.html', show_text=show_text)


@app.route('/girl/bowl')
def bowl_table():
    table_main(selected_lodge)
    print("table_visit: ", table_visit)
    return render_template('girl_table.html', show_text=show_text)


@app.route('/girl/dad_bowl')
def dad_bowl():
    # dad_porridge()
    return render_template('dad_bowl_page.html', show_text=show_text)


@app.route('/girl/mom_bowl')
def mom_bowl():
    # mom_porridge()
    return render_template('mom_bowl_page.html', show_text=show_text)


@app.route('/girl/baby_bowl')
def baby_bowl():
    # baby_porridge()
    return render_template('baby_bowl_page.html', show_text=show_text)


@app.route('/girl/chair')
def chairs():
    # chair_main()
    return render_template('chairs.html', show_text=show_text)


@app.route('/girl/dad_chair')
def dad_chairs():
    dad_chair()
    return render_template('dad_chair_page.html', show_text=show_text)


@app.route('/girl/mom_chair')
def mom_chairs():
    # mom_chair()
    return render_template('mom_chair_page.html', show_text=show_text)


@app.route('/girl/baby_chair')
def baby_chairs():
    # baby_chair()
    print("chair_visit main file: ", chair_visit)
    return render_template('baby_chair_page.html', show_text=show_text)


@app.route('/girl/baby_chair2')
def baby_chairs2():
    # baby_chair2()
    return render_template('baby_chair_page2.html', show_text=show_text)


@app.route('/girl/bed')
def beds():
    bed_main()
    return render_template('beds.html', show_text=show_text)


@app.route('/girl/dad_bed')
def dad_bed():
    # dad_bed_func()
    return render_template('dad_bed_page.html', show_text=show_text)


@app.route('/girl/mom_bed')
def mom_bed():
    # mom_bed_func()
    return render_template('mom_bed_page.html', show_text=show_text)


@app.route('/girl/baby_bed')
def baby_bed():
    # baby_bed_func()
    return render_template('baby_bed_page.html', show_text=show_text)


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@app.route('/bear_1st')
def bear_1st():
    # bear_1st_func()
    return render_template('bear_1st_page.html', show_text=show_text)


# @app.route('/girl/bear_2nd')
@app.route('/bear_2nd')
def bear_2nd():
    # bear_2nd_func()
    return render_template('bear_2nd_page.html', show_text=show_text)


# @app.route('/girl/bear_3th')
@app.route('/bear_3rd')
def bear_3th():
    # bear_3rd_func()
    return render_template('bear_3th_page.html', show_text=show_text)


# @app.route('/girl/bear_4th')
@app.route('/bear_4th')
def bear_4th():
    # bear_4th_func()
    return render_template('bear_4th_page.html', show_text=show_text)


# @app.route('/girl/bear_5th')
@app.route('/bear_5th')
def bear_5th():
    # bear_5th_func()
    return render_template('bear_5th_page.html', show_text=show_text)


# @app.route('/girl/bear_6th')
@app.route('/bear_6th')
def bear_6th():
    # bear_6th_func()
    return render_template('bear_6th_page.html', show_text=show_text)


@app.route('/bear_7th')
def bear_7th():
    # bear_7th_func()
    return render_template('bear_7th_page.html', show_text=show_text)


# @app.route('/girl/bear_8th')
@app.route('/bear_8th')
def bear_8th():
    # bear_8th_func()
    return render_template('bear_8th_page.html', show_text=show_text)


# @app.route('/girl/bear_9th')
@app.route('/bear_9th')
def bear_9th():
    # bear_9th_func()
    global selected_character
    print("selected_character: ", selected_character)
    return render_template('bear_9th_page.html', character=selected_character, show_text=show_text)


@app.route('/girl/bear_10th')
def bear_10th():
    # bear_10th_func()
    return render_template('bear_10th_page.html', show_text=show_text)


@app.route('/girl/bear_11th')
def bear_11th():
    # bear_11th_func()
    return render_template('bear_11th_page.html', show_text=show_text)


@app.route('/girl/bear_12th')
def bear_12th():
    # bear_12th_func()
    if selected_lodge == 'lodge1':
        return render_template('bear_12th_page1.html', show_text=show_text)
    else:
        return render_template('bear_12th_page2.html', show_text=show_text)


@socketio.on('dice_face_in_young_action')
def dice_face_in_young_action(dice_face_str):
    global emotionShow_pub
    global gesturePlay_servc
    global stop_triggered_flag
    print("dice_face_str: " + dice_face_str)
    handle_gesture_play("QT/neutral", 2)
    # gesturePlay_servc("QT/neutral", 2)

    rospy.sleep(1)
    # talktext_pub.publish(dice_face_str)
    print("stop_triggered_flag: ", stop_triggered_flag)
    if dice_face_str == 'Jumping Jacks':
        handle_speech_say("Let's do 10 jumping jacks!")
        rospy.sleep(2)

        # Run the jumping jacks logic in a separate thread
        threading.Thread(target=execute_jumping_jacks).start()
        # threading.start()

    elif dice_face_str == 'Count to 5':
        # talktext_pub.publish("Let's deep breathe for five seconds")
        handle_speech_say("Let's deep breathe for five seconds")
        rospy.sleep(2)
        # talktext_pub.publish("1, 2, 3, 4, 5")
        handle_speech_say("1, 2, 3, 4, 5")
        # gesturePlay_pub.publish("breathing_soomin")
        # gesturePlay_servc("breathing_soomin", 1.5)
        handle_gesture_play("breathing_soomin", 1.5)

    elif dice_face_str == 'Sing a Song':
        # talktext_pub.publish("Let's sing a song!")
        music = ["spider", "ABC", "mcdonald", "twinkle", "wheels"]
        random_song = random.choice(music)
        random_song = "wheels"
        print("random_song: " + random_song)
        if str(random_song) == "spider":
            # talktext_pub.publish("Let's sing Incy Wincy Spider")
            # handle_speech_say("Let's sing Incy Wincy Spider")
            handle_speech_say("Let's sing a song")
            rospy.sleep(2)
            # gesturePlay_pub.publish("IncyWincySpider")
            handle_gesture_play("IncyWincySpider", 1)
            # audioPlay_pub.publish(random_song)
            handle_audio_play(random_song)

        elif str(random_song) == "ABC":
            # talktext_pub.publish("Let's sing ABC")
            # handle_speech_say("Let's sing ABC")
            handle_speech_say("Let's sing a song")
            rospy.sleep(2)
            # gesturePlay_pub.publish("ABCsong")
            handle_gesture_play("ABCsong", 1)
            # audioPlay_pub.publish(random_song)
            handle_audio_play(random_song)

        elif str(random_song) == "mcdonald":
            # talktext_pub.publish("Let's sing Old MacDonald")
            # handle_speech_say("Let's sing Old MacDonald")
            handle_speech_say("Let's sing a song")
            rospy.sleep(2)
            # gesturePlay_pub.publish("Old_MacDonald")
            handle_gesture_play("Old_MacDonald", 1)
            # audioPlay_pub.publish(random_song)
            handle_audio_play(random_song)

        elif str(random_song) == "twinkle":
            # talktext_pub.publish("Let's sing twinkle twinkle little star")
            # handle_speech_say("Let's sing twinkle twinkle")
            handle_speech_say("Let's sing a song")
            rospy.sleep(2)
            # gesturePlay_pub.publish("twinkletwinklelittlestar")
            handle_gesture_play("twinkletwinklelittlestar", 1)
            # audioPlay_pub.publish(random_song)
            handle_audio_play(random_song)

        elif str(random_song) == "wheels":
            # talktext_pub.publish("Let's sing Wheels on the bus")
            # handle_speech_say("Let's sing Wheels on the bus")
            handle_speech_say("Let's sing a song")
            rospy.sleep(2)
            # gesturePlay_pub.publish("Wheels_bus")
            handle_gesture_play("Wheels_bus", 1)
            # audioPlay_pub.publish(random_song)
            handle_audio_play(random_song)



    elif dice_face_str == 'Wiggle':
        # talktext_pub.publish("Let's wiggle our body!")
        handle_speech_say("Let's wiggle our body for ten seconds!")
        rospy.sleep(2)
        # talktext_pub.publish("1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
        handle_speech_say("1, 2, 3, 4, 5, 6, 7, 8, 9, 10")
        # gesturePlay_servc("wiggle_body", 1.5)
        handle_gesture_play("wiggle_body", 1.5)
        # rospy.sleep(2)


    elif dice_face_str == 'Bear Hug':
        # talktext_pub.publish("Let's have a bear hug!")
        handle_speech_say("Let's have a bear hug!")
        rospy.sleep(2)
        # talktext_pub.publish("1, 2, 3, 4, 5")
        handle_speech_say("1, 2, 3, 4, 5")
        rospy.sleep(1)
        # gesturePlay_servc("hug", 1.3)
        handle_gesture_play("hug", 1.3)



    elif dice_face_str == 'High Five':
        # talktext_pub.publish("Give me a high five!")
        handle_speech_say("Let's have a high five!")
        rospy.sleep(2)
        # gesturePlay_servc("high_five_soomin", 1.5)
        handle_gesture_play("high_five_soomin", 1.5)

    # speechConfig_servc('en-US', 105, 75)
    rospy.sleep(2)
    stop_triggered_flag = False


@socketio.on('dice_face_in_young_emotion')
def dice_face_in_young_emotion(dice_face_str):
    global emotionShow_pub
    global gesturePlay_servc
    # gesturePlay_servc("QT/neutral", 2)
    handle_gesture_play("QT/neutral", 2)
    rospy.sleep(1)
    # talktext_pub.publish(dice_face_str)
    handle_speech_say(dice_face_str)
    if dice_face_str == 'anger':
        rospy.sleep(2)
        # emotionShow_pub.publish("QT/angry")
        handle_emotion_play("QT/angry")
        rospy.sleep(1)
        # gesturePlay_servc("QT/angry", 1)
        handle_gesture_play("QT/angry", 1)

    elif dice_face_str == 'happy':
        rospy.sleep(2)
        # emotionShow_pub.publish("QT/happy")
        # gesturePlay_servc("QT/happy", 1)
        handle_emotion_play("QT/happy")
        handle_gesture_play("QT/happy", 1)


    elif dice_face_str == 'sad':
        rospy.sleep(2)
        # emotionShow_pub.publish("QT/sad")
        # gesturePlay_servc("soomin_sad", 1)
        handle_emotion_play("QT/sad")
        handle_gesture_play("soomin_sad", 1)

    elif dice_face_str == 'scared':
        rospy.sleep(2)
        # emotionShow_pub.publish("QT/afraid")
        # gesturePlay_servc("QT/afraid", 1)
        handle_emotion_play("QT/afraid")
        handle_gesture_play("QT/afraid", 1)

    elif dice_face_str == 'surprised':
        rospy.sleep(2)
        # emotionShow_pub.publish("QT/surprise")
        # gesturePlay_servc("soomin_surprise",2)
        handle_emotion_play("QT/surprise")
        handle_gesture_play("soomin_surprise", 2)


    else:
        # emotionShow_pub.publish("QT/disgusted")
        # gesturePlay_servc("uwaterloo-1/kickstart/Ugh",1.5)
        handle_emotion_play("QT/disgusted")
        handle_gesture_play("uwaterloo-1/kickstart/Ugh", 1.5)

    rospy.sleep(2)


@socketio.on('dice_face_in_old_emotion')
def dice_face_in_old_emotion(dice_face_str):
    global emotionShow_pub
    global gesturePlay_servc

    rospy.sleep(1)
    talktext_pub.publish(dice_face_str)
    if dice_face_str == 'curious':
        rospy.sleep(1.5)
        # emotionShow_pub.publish("QT/breathing_exercise")
        handle_emotion_play("QT/breathing_exercise")
        rospy.sleep(3.5)
        # talktext_pub.publish("what makes you curious?")
        handle_speech_say("what makes you curious?")

    elif dice_face_str == 'silly':
        rospy.sleep(1.5)
        # emotionShow_pub.publish("QT/blowing_raspberry")
        handle_emotion_play("QT/blowing_raspberry")
        rospy.sleep(1.5)
        # gesturePlay_servc("soomin_silly", 2)
        handle_gesture_play("soomin_silly", 3)
        rospy.sleep(3)
        # talktext_pub.publish("when do you feel silly?")
        handle_speech_say("when do you feel silly?")

    elif dice_face_str == 'excited':
        rospy.sleep(2)
        # emotionShow_pub.publish("QT/happy")
        handle_emotion_play("QT/happy")
        rospy.sleep(1.5)
        # gesturePlay_servc("QT/point_front", 1)
        handle_gesture_play("QT/emotions/hoora", 1)
        rospy.sleep(3.8)
        # talktext_pub.publish("Who makes you feel excited?")
        handle_speech_say("Who makes you feel excited?")

    elif dice_face_str == 'tired':
        rospy.sleep(1.5)
        # emotionShow_pub.publish("QT/yawn")
        handle_emotion_play("QT/yawn")
        rospy.sleep(1)
        # gesturePlay_servc("QT/yawn", 1)
        handle_gesture_play("QT/yawn", 1)
        rospy.sleep(3.5)
        # talktext_pub.publish("When do you feel tired?")
        handle_speech_say("When do you feel tired?")

    elif dice_face_str == 'frustrated':
        rospy.sleep(2)
        # emotionShow_pub.publish("QT/scream")
        handle_emotion_play("QT/scream")
        # rospy.sleep(2)
        # talktext_pub.publish("ahhh")
        # gesturePlay_servc("frustration", 1.5)
        handle_gesture_play("frustration", 1.5)
        # talktext_pub.publish("ahhh")
        rospy.sleep(4)
        # talktext_pub.publish("When do you feel frustrated?")
        handle_speech_say("When do you feel frustrated?")

    else:
        rospy.sleep(2)
        # emotionShow_pub.publish("question")
        handle_emotion_play("question")
        rospy.sleep(1)
        # talktext_pub.publish("What makes you feel confused?")
        handle_speech_say("What makes you feel confused?")


@socketio.on('dice_5w1h')
def dice_5w1h(dice_face_str):
    global emotionShow_pub
    global gesturePlay_servc
    rand_var = random.randint(0, 4)
    # handle_gesture_play(Idle_gestures[rand_var], 1.5)
    gesturePlay_pub.publish(Idle_gestures[rand_var])
    rospy.sleep(1)
    print("dice_5w1h: " + dice_face_str)
    # talktext_pub.publish(dice_face_str)
    handle_speech_say(dice_face_str)


@socketio.on('dice_board')
def dice_board(dice_face_str):
    global emotionShow_pub
    global gesturePlay_servc

    rospy.sleep(1)

    gesturePlay_pub.publish("idle_arms_up_1")

    numbers = ["zero", "one", "two", "three", "four", "five", "six"]

    s = "" if dice_face_str == '1' else "s"

    handle_speech_say(f"Move your piece on the board by {numbers[int(dice_face_str)]} step{s}!")
    rospy.sleep(1)

    gesturePlay_pub.publish("idle_test_1")
    rospy.sleep(1)

@socketio.on('dice_question')
def dice_ask_question(question):
    print(f"dice_question {question}")
    gesturePlay_pub.publish(get_short_idle_gesture())

    handle_speech_say(question)


@app.route('/dice_action_young_start')
def dice_action_young_start():
    # talktext_pub.publish("Let's roll the dice")
    handle_speech_say("Let's roll the dice")
    return render_template('dice_action_young.html')


@app.route('/dice_emotion_young_start')
def dice_emotion_young_start():
    # talktext_pub.publish("Let's roll the dice")
    handle_speech_say("Let's roll the dice")
    return render_template('dice_emotion_young.html')


@app.route('/dice_emotion_old_start')
def dice_emotion_old_start():
    # talktext_pub.publish("Let's roll the dice")
    handle_speech_say("Let's roll the dice")
    return render_template('dice_emotion_old.html')


@app.route('/dice_5w1h')
def dice_5w1h():
    # talktext_pub.publish("Let's roll the dice")
    handle_speech_say("Lets play around with wh questions")
    return render_template('dice_5w1h.html')


@app.route('/dice_5w1h_1')
def dice_5w1h_1():
    # talktext_pub.publish("Let's roll the dice")
    handle_speech_say("Let's roll the dice")
    return render_template('dice_why_when_how.html')


@app.route('/dice_5w1h_2')
def dice_5w1h_2():
    # talktext_pub.publish("Let's roll the dice")
    handle_speech_say("Let's roll the dice")
    return render_template('dice_what_who_where.html')


@app.route('/dice_board')
def dice_board():
    # talktext_pub.publish("Let's roll the dice")
    handle_speech_say("Let's roll the dice")
    return render_template('dice_board_game.html')


######################################################################################### red riding hood  ############################################################################################
@app.route('/story_game_old')
def story_old_main():
    handle_speech_say("Lets choose a story")
    return render_template('old_story_main.html')


@app.route('/red_riding_start_page')
def red_riding_start():
    print("red_riding1 start")
    # talktext_pub.publish("Lets start the story")
    return render_template('red_riding/story_text_select.html')


@app.route('/red_riding_hood1')
def red_riding1():
    print("red_riding1 route function")
    red_riding_first()
    return render_template('red_riding/red_riding1.html', show_text=show_text)


@socketio.on('red_riding_first')
def red_riding_first():
    rospy.sleep(1.0)
    print("here")
    gesturePlay_pub.publish(get_short_idle_gesture())
    talktext_pub.publish(
        "There once was a girl known as Little Red Riding Hood. and she always wore a red riding cape wherever she went.")
    print("...")


@socketio.on('story_line')
def story_speak(msg, sound):
    rospy.sleep(1.0)
    print("msg:", msg)

    # Split the text at punctuation marks into chunks
    # chunks = text_split(msg)
    gesturePlay_pub.publish(get_short_idle_gesture())
    talktext_pub.publish(msg)
    if sound != "":
        rospy.sleep(1.5)
        audioPlay_pub.publish(sound)



######################################################################################### break, at talks     ############################################################################################
#

@app.route('/break')
def break_fucn():
    # talktext_pub.publish("Let's roll the dice")
    handle_speech_say("Let's take a break")
    # gesturePlay_servc("head_natural", 1.5)
    # gesturePlay_pub.publish("head_natural")
    return render_template('break.html')


@app.route('/at_talks')
def at_talks_func():
    # talktext_pub.publish("Let's roll the dice")
    # handle_speech_say("Let's roll the dice")
    return render_template('at_talks.html')


######################################################################################### story game - young  ##############################################################
@app.route('/story_game_young')
def story_young_main():
    handle_speech_say("Lets choose a story")
    return render_template('young_story_main.html')


############ Brown bear

@app.route('/brown_bear')
def story_young():
    talktext_pub.publish("I will tell you a story")
    return render_template('brown_bear.html')


@app.route('/brown_bear2')
def story_young2():
    # gesturePlay_pub.publish(get_short_idle_gesture())
    return render_template('brown_bear2.html')


@app.route('/brown_bear3')
def story_young3():
    # gesturePlay_pub.publish(get_short_idle_gesture())
    return render_template('brown_bear3.html')


@app.route('/brown_bear4')
def story_young4():
    # gesturePlay_pub.publish(get_short_idle_gesture())
    return render_template('brown_bear4.html')


@app.route('/brown_bear5')
def story_young5():
    return render_template('brown_bear5.html')


@app.route('/brown_bear6')
def story_young6():
    return render_template('brown_bear6.html')


@app.route('/brown_bear7')
def story_young7():
    return render_template('brown_bear7.html')


@app.route('/brown_bear8')
def story_young8():
    return render_template('brown_bear8.html')


@app.route('/brown_bear9')
def story_young9():
    return render_template('brown_bear9.html')


@app.route('/brown_bear10')
def story_young10():
    return render_template('brown_bear10.html')


@socketio.on('brown_talk')
def speech_brown_bear(text, sleep_time, wait=False):
    print("brown_talk: ", text, sleep_time)
    rospy.sleep(sleep_time)
    # talktext_pub.publish(text)

    gesturePlay_pub.publish(get_short_idle_gesture())

    handle_speech_say(text)


############ Goodnight moon
@app.route('/goodnight')
def story_young_moon():
    # talktext_pub.publish("I will tell you a story")
    return render_template('/goodnight/goodnight_moon.html')


@app.route('/goodnight2')
def story_young_moon2():
    return render_template('/goodnight/goodnight_moon2.html')


@app.route('/goodnight3')
def story_young_moon3():
    return render_template('/goodnight/goodnight_moon3.html')


@app.route('/goodnight4')
def story_young_moon4():
    return render_template('/goodnight/goodnight_moon4.html')


@app.route('/goodnight5')
def story_young_moon5():
    return render_template('/goodnight/goodnight_moon5.html')


@app.route('/goodnight6')
def story_young_moon6():
    return render_template('/goodnight/goodnight_moon6.html')


@app.route('/goodnight7')
def story_young_moon7():
    return render_template('/goodnight/goodnight_moon7.html')


@app.route('/goodnight8')
def story_young_moon8():
    return render_template('/goodnight/goodnight_moon8.html')


@app.route('/goodnight9')
def story_young_moon9():
    return render_template('/goodnight/goodnight_moon9.html')


@app.route('/goodnight10')
def story_young_moon10():
    return render_template('/goodnight/goodnight_moon10.html')


@app.route('/goodnight11')
def story_young_moon11():
    return render_template('/goodnight/goodnight_moon11.html')


########################################################################################  Yes or No, Inference  ##############################################################

@socketio.on('yes_or_no')
def speech_yes_or_no(text, sleep_time):
    print("speech_yes_or_no: ", text, sleep_time)
    rospy.sleep(sleep_time)
    gesturePlay_pub.publish(get_short_idle_gesture())
    talktext_pub.publish(text)

@app.route('/yes_no_young')
def yes_no_young():
    # talktext_pub.publish("I will tell you a story")
    return render_template('yes_no_young.html')


@app.route('/yes_no_old')
def yes_no_old():
    # talktext_pub.publish("I will tell you a story")
    return render_template('yes_no_old.html')


############ Inference game

@app.route('/inference')
def inference_fucn():
    talktext_pub.publish("Lets play inference games")
    # gesturePlay_servc("head_natural", 1.5)
    return render_template('inference/inference1.html')

@socketio.on('inference')
def speech_inference(text, sleep_time):
    """
    Reads out the inference game text.
    Every two sentences the robot will perform an idle gesture.

    """
    print("speech_inference: ", text, sleep_time)
    rospy.sleep(sleep_time)
    # gesturePlay_pub.publish(get_short_idle_gesture())
    # behaviorTalk_servc(text)

    # Split the text at punctuation marks into chunks\
    chunks = text_split(text)

    for chunk in chunks:
        gestureStop_servc()
        gesturePlay_pub.publish(get_short_idle_gesture())
        behaviorTalk_servc(chunk)

#


@socketio.on('start_talk')
def first_talk_robot_interactive():
    # Display two characters. Becomes the main character of the story
    print("func first_talk_robot_interactive")
    rospy.sleep(1.0)
    global talktext_pub
    talktext_pub.publish("Lets start the story!")


@socketio.on('first_page')
def second():
    # global talktext_pub
    # rospy.sleep(2.0)
    talktext_pub.publish("Once upon a time lived Goldilocks and The Three Bears.")


@socketio.on('girl_lodge')
def third_girl():
    # global talktext_pub
    talktext_pub.publish("One day, Goldilocks went for a walk in the forest and found a house.")
    rospy.sleep(5.0)
    audioPlay_pub.publish('QT/knock')
    rospy.sleep(1.5)
    behaviorTalk_servc("She knocked, and when nobody answered, she decided to go inside.")


@socketio.on('girl_table')
def table_main(msg):
    print("msg: ", msg)
    selected_lodge = msg
    print("porridge_visited: ", porridge_visited[0])

    socketio.emit('checking_visit', "String ", broadcast=True)
    print("msg: ", selected_lodge)

    if (porridge_visited[0] == False and selected_lodge != " "):
        # If this is the first visit on this page, robot speaks to choose one bowl
        rospy.sleep(2.0)
        talktext_pub.publish("At the table, there were three bowls of porridge. Goldilocks was hungry.")


@socketio.on('dad_porridge')
def dad_porridge():
    emotionShow_pub.publish("QT/disgusted")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/Ugh")
    porridge_visited[0] = True
    talktext_pub.publish("Goldilocks tasted the porridge from the large bowl. This porridge is too salty")


@socketio.on('mom_porridge')
def mom_porridge():
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/No_my")
    porridge_visited[0] = True
    talktext_pub.publish("Goldilocks tasted the porridge from the medium sized bowl. “This porridge is too sweet!")


@socketio.on('baby_porridge')
def baby_porridge():
    emotionShow_pub.publish("QT/happy")
    gesturePlay_pub.publish("QT/happy")
    porridge_visited[0] = True
    talktext_pub.publish(
        "Goldilocks tasted the porridge from the small bowl. “This porridge is just right,” Goldilocks said and ate it all up.")


@socketio.on('chair')
def chair_main():
    print("chair connected")
    print("chair_visited: ", chair_visited[0])
    print("chair_visit: ", chair_visit)
    socketio.emit('number', chair_visit, broadcast=True)
    if (chair_visited[0] == False):
        talktext_pub.publish("Goldilocks felt tired, so Goldilocks walked into the living room and saw three chairs.")


@socketio.on('dad_chair')
def dad_chair():
    print("here")
    print("here 2")
    print("chair_visit: ", chair_visit)
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/hmm")
    talktext_pub.publish("Goldilocks sat in the large chair to rest her feet. “This chair is too big!")
    chair_visited[0] = True


@socketio.on('mom_chair')
def mom_chair():
    print("chair_visit: ", chair_visit)
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/cross_arm")
    chair_visited[0] = True
    talktext_pub.publish("Goldilocks sat in the medium sized chair. This chair is too big, too!")


@socketio.on('baby_chair')
def baby_chair():
    global baby_chair_visit_check
    print("chair_visit: ", chair_visit)
    if (baby_chair_visit_check == False):
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
    talktext_pub.publish("Just as Goldilocks settled down into the chair to rest, it broke into pieces!")


@socketio.on('bed')
def bed_main():
    print("bed_visited: ", bed_visited[0])
    socketio.emit('number', bed_visit, broadcast=True)
    if (bed_visited[0] == False):
        # If this is the first visit on this page, robot speaks to choose one bowl
        print("bed enter")
        talktext_pub.publish("By now, Goldilocks was very tired, Goldilocks went upstairs to the bedroom.")


@socketio.on('dad_bed')
def dad_bed_func():
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/cross_arm")
    bed_visited[0] = True
    talktext_pub.publish("Goldilocks lay down on the large bed. “This bed is too hard!” ")


@socketio.on('mom_bed')
def mom_bed_func():
    emotionShow_pub.publish("QT/confused")
    gesturePlay_pub.publish("uwaterloo-1/kickstart/hmm")
    bed_visited[0] = True
    talktext_pub.publish("Goldilocks lay down on the medium sized bed. This bed is too soft!")


@socketio.on('baby_bed')
def baby_bed_func():
    gesturePlay_pub.publish("soomin_yawn")
    rospy.sleep(2.5)
    emotionShow_pub.publish("QT/yawn")
    bed_visited[0] = True
    talktext_pub.publish(
        "Goldilocks lay down on the small bed. This bed is just right. Goldilocks curled up and fell asleep.")


# # # # # # # # # # # # Bear  # # # # # # # # # # # # # # # # # # #
@socketio.on('bear_1st')
def bear_1st_func():
    talktext_pub.publish("As Goldilocks was sleeping, The Three Bears came home.")

    gesturePlay_pub.publish(get_short_idle_gesture())

    porridge_visited[0] = False
    chair_visited[0] = False
    bed_visited[0] = False


@socketio.on('bear_2nd')
def bear_2nd_func():
    talktext_pub.publish("Someone’s been eating my porridge, growled Daddy Bear.")
    rospy.sleep(4)
    # audioPlay_servc("QT/growl_3", "")
    audioPlay_pub.publish('QT/growl_3')


@socketio.on('bear_3rd')
def bear_3rd_func():
    talktext_pub.publish("Someone’s been eating my porridge, said Mummy Bear.")

    gesturePlay_pub.publish(get_short_idle_gesture())


@socketio.on('bear_4th')
def bear_4th_func():
    talktext_pub.publish("Someone’s been eating my porridge and it’s all gone!. Cried Baby Bear")
    rospy.sleep(4.0)
    audioPlay_pub.publish('QT/cry2_increased')


@socketio.on('bear_5th')
def bear_5th_func():
    talktext_pub.publish("Someone’s been sitting in my chair!. Growled Daddy Bear.")
    rospy.sleep(4.0)
    audioPlay_pub.publish('QT/growl_3')


@socketio.on('bear_6th')
def bear_6th_func():
    talktext_pub.publish("Someone’s been sitting in my chair!” said Mummy Bear.")

    gesturePlay_pub.publish(get_short_idle_gesture())


@socketio.on('bear_7th')
def bear_7th_func():
    talktext_pub.publish("Someone’s been sitting in my chair and it’s broken!. Cried Baby Bear.")
    rospy.sleep(3.5)
    audioPlay_pub.publish('QT/cry2_increased')


@socketio.on('bear_8th')
def bear_8th_func():
    talktext_pub.publish(
        "When they got upstairs to the bedroom, Daddy Bear growled. Someone’s been sleeping on my bed.")
    rospy.sleep(2.0)
    audioPlay_pub.publish('QT/growl_3')


@socketio.on('bear_9th')
def bear_9th_func():
    talktext_pub.publish("Someone’s been sleeping on my bed too, said the Mummy Bear")

    gesturePlay_pub.publish(get_short_idle_gesture())

@socketio.on('bear_10th')
def bear_10th_func():
    talktext_pub.publish("Someone’s been sleeping in my bed, and she’s still there!. Cried Baby Bear.")
    rospy.sleep(3.5)
    audioPlay_pub.publish('QT/cry2_increased')


@socketio.on('bear_11th')
def bear_11th_func():
    talktext_pub.publish("Just then Goldilocks woke up and saw The Three Bears.")
    # rospy.sleep(3)
    # audioPlay_servc('QT/scream_low', "")
    rospy.sleep(3)
    audioPlay_pub.publish('QT/helpme')
    rospy.sleep(0.5)
    behaviorTalk_servc("She screamed.")


@socketio.on('bear_12th')
def bear_12th_func():
    talktext_pub.publish(
        "Goldilocks ran down the stairs and into the forest. And she never went back into the woods again.")

    gesturePlay_pub.publish(get_short_idle_gesture())


######################################################################################### Negin     ############################################################################################
# Emotion game1
def emotion_card(id):
    global talktext_pub
    global speechSay_pub
    global emotionShow_pub
    global gesturePlay_pub
    # gesturePlay_servc("QT/neutral", 2)
    if id == 0:
        talktext_pub.publish("angry!")

        rospy.sleep(3.0)
        emotionShow_pub.publish("QT/angry")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/angry")
        emotionShow_pub.publish("QT/angry")
        # r1 = random.randint(0,len(angry)-1)
        # talktext_pub.publish(angry[r1])
    elif id == 1:
        talktext_pub.publish("happy!")
        rospy.sleep(3.0)
        emotionShow_pub.publish("QT/happy")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/happy")
        emotionShow_pub.publish("QT/happy")
        # r2 = random.randint(0,len(happy)-1)
        # talktext_pub.publish(happy[r2])
    elif id == 2:
        talktext_pub.publish("excited!")
        rospy.sleep(3.0)
        emotionShow_pub.publish("QT/happy_blinking")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/hoora")
        emotionShow_pub.publish("QT/happy_blinking")

    elif id == 3:
        talktext_pub.publish("saed")
        rospy.sleep(3.0)
        emotionShow_pub.publish("QT/sad")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/sad")
        emotionShow_pub.publish("QT/sad")
        # r4 = random.randint(0,len(sad)-1)
        # talktext_pub.publish(sad[r4])
    elif id == 4:
        talktext_pub.publish("scared!")
        rospy.sleep(3.0)
        emotionShow_pub.publish("QT/afraid")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/afraid")
        emotionShow_pub.publish("QT/afraid")
        # r5 = random.randint(0,len(scared)-1)
        # talktext_pub.publish(scared[r5])
    elif id == 5:
        talktext_pub.publish("sheye")
        rospy.sleep(3.0)
        emotionShow_pub.publish("QT/shy")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/shy")

    if (id < 6 and id > -1):
        rospy.sleep(8)
        talktext_pub.publish("Look at the tablet, which one is " + " " + emotion_dictionary[id])


emotion_dictionary = {0: "angry", 1: "happy", 2: "excited", 3: "sad", 4: "scared", 5: "shy"}


def object_card(id):
    global action
    if action =="tidy":
        action = "tidy up"

    talktext_pub.publish(action)
    rospy.sleep(3)
    talktext_pub.publish("Look at the tablet, click on the picture")


def young_emotion_card(id):
    print(id)
    global talktext_pub
    global speechSay_pub
    global emotionShow_pub
    global gesturePlay_pub
    # gesturePlay_servc("QT/neutral", 2)
    if id == 0:
        talktext_pub.publish("angry!")

        rospy.sleep(2.0)
        emotionShow_pub.publish("QT/angry")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/angry")
    elif id == 1:
        talktext_pub.publish("happy!")
        rospy.sleep(2.0)
        emotionShow_pub.publish("QT/happy")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/happy")
    elif id == 2:
        talktext_pub.publish("excited!")
        rospy.sleep(2.0)
        emotionShow_pub.publish("QT/happy_blinking")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/hoora")

    elif id == 3:
        talktext_pub.publish("saed")
        rospy.sleep(2.0)
        emotionShow_pub.publish("QT/sad")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/sad")
    elif id == 4:
        talktext_pub.publish("scared!")
        rospy.sleep(2.0)
        emotionShow_pub.publish("QT/afraid")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/afraid")
    elif id == 5:
        talktext_pub.publish("sheye")
        rospy.sleep(2.0)
        emotionShow_pub.publish("QT/shy")
        rospy.sleep(1.0)
        gesturePlay_pub.publish("/QT/emotions/shy")

    rospy.sleep(3.0)
    talktext_pub.publish("Look at the tablet, click on the picture")


@app.route('/request', methods=['POST'])
def request_callback():
    global game
    global selected
    if (game == "emotion_game1"):  # one emotion card + which face is this

        global selected_emotion
        id = request.form['emotion']
        print("ID: " + id)
        data = emotion_dictionary[int(id)]
        selected_emotion = data
        emotion = list(emotions.keys())[list(emotions.values()).index(data)]
        if selected == 0 and int(id) < 7:
            young_emotion_card(int(id))
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
            print("'/request' action: ", action)
            socketio.emit('update image', {'path': [path + "/action_cards/" + action + ".png"]}, broadcast=True)
            object_card(action)
    return "pass"

################################################################  Emotion game for older age group   ###################################################3


emotions = {0: "happy", 1: "angry", 2: "scared", 3: "excited", 4: "shy", 5: "sad"}

happy = {'pet_happy': "I like to cuddle and play with my pets when I'm happy",
         'park_smile': "Going to the park makes me happy.",
         'friend_happy': "I feel happy when I play with my friends.",
         'toy': "I feel happy when I get my favorite toy.",
         'family_happy': "I’m happy when I spend time with my family",
         'smile_birthday': "I feel happy when I get presents on my birthday.",
         'activity_happy': "I like to do my favorite activity when I feel happy."}

sad = {'sad_family': "I feel sad when I miss my family.",
       'sad_friend': "I feel sad when my friends don't share their toys with me.",
       'sad_game': "I feel sad when I lose a game.",
       'sad_snack': "I feel sad when I don’t get my favorite snack.",
       'sad_outside': "I feel sad when I can’t go outside to play.",
       'sad_birthday': "I feel sad when someone doesn’t wish me a Happy Birthday.",
       'sad_toy': "I get sad when my favorite toy is lost or broken.",
       'friend_sad': "I feel sad when someone is being mean to me."}

angry = {'angry_toy': "I feel angry when someone takes my toy without asking.",
         'game': "I feel angry when I don’t get a turn playing a game.",
         'listen': "I feel angry when people aren’t listening to me.",
         'homework': "I feel angry when I don’t understand my homework.",
         'friend': "I feel angry when my friends don’t want to play the game I like.",
         'block': "I feel angry when my building blocks keep falling down.",
         'friend': "I feel angry when my friend is busy and can’t play with me."}

shy = {'new': "I get shy when I meet new people.",
       'class': "I get shy when I have to read in front of my class.",
       'question': "I feel shy when I am asked to answer a question in school.",
       'perform': "I feel shy when I have to perform on stage in front of everyone.",
       'phone': "I feel shy when I have to talk on the phone.",
       # 'shy': "I feel shy when I wear something new.",
       'group': "I feel shy when I have to join a new group of friends for an activity."}

excited = {'travel': "I feel excited when I am going on vacation with my family.",
           'amusement':"I feel excited going to an amusement park",
           'beach':"I feel excited when I go to the beach and build sandcastles",
           'birthday':"I feel excited when I go to a birthday party",
           'game':"I feel excited when I win a game",
           'movie':"I feel excited when I have movie night with my family",
           'outside':"I feel excited when I go on adventures outside",
           'rainbow':"I feel excited when I see a rainbow"
           }

scared = {
    'dark': "I feel scared when it’s dark outside.",
    'doctor': "I feel scared when I have to go to the doctor.",
    'lost': "I feel scared when I get lost.",
    'alone': "I feel scared when I am alone.",
    'dream': "I feel scared when I have a bad dream.",
    'thunder': "I feel scared when I hear thunder and lightning",
    'myself': "I feel scared when I have to do something by myself for the first time.",
    'loud': "I feel scared when I hear a loud noise."
}


def random_image_selector(id):
    l = []
    x = id
    y = 5 - x
    print(emotions[x])
    l.append(path + "emotions/" + emotions[x] + ".jpg")
    l.append(path + "emotions/" + emotions[y] + ".jpg")
    return l



happy_dict = list(range(0, len(happy)))
random.shuffle(happy_dict)
angry_dict = list(range(0, len(angry)))
random.shuffle(angry_dict)
scared_dict = list(range(0, len(scared)))
random.shuffle(scared_dict)
excited_dict = list(range(0, len(excited)))
random.shuffle(excited_dict)
shy_dict = list(range(0, len(shy)))
random.shuffle(shy_dict)
sad_dict = list(range(0, len(sad)))
random.shuffle(sad_dict)

emotion_var_old_happy =0
emotion_var_old_angry=0
emotion_var_old_scared=0
emotion_var_old_excited=0
emotion_var_old_shy=0
emotion_var_old_sad = 0

################ emotion card game for older age group ##########################
def random_image(id):
    global var
    global emotion_var_old_happy,emotion_var_old_angry, emotion_var_old_scared,emotion_var_old_excited, emotion_var_old_shy,emotion_var_old_sad
    print("--------------------random_image-----------------------------------")
    print("id:  ",id)
    if id == 0:
        em = list(happy.keys())[emotion_var_old_happy]
        var = happy[em]
        emotion_var_old_happy+=1
        if(emotion_var_old_happy == len(happy)):
            emotion_var_old_happy = 0
    elif id == 1:
        em = list(angry.keys())[emotion_var_old_angry]
        var = angry[em]
        emotion_var_old_angry+=1
        if (emotion_var_old_angry == len(angry)):
            emotion_var_old_angry = 0
    elif id == 2:
        em = list(scared.keys())[emotion_var_old_scared]
        var = scared[em]
        emotion_var_old_scared+=1
        if (emotion_var_old_scared == len(scared)):
            emotion_var_old_scared = 0
    elif id == 3:
        em = list(excited.keys())[emotion_var_old_excited]
        var = excited[em]
        emotion_var_old_excited+=1
        if (emotion_var_old_excited == len(excited)):
            emotion_var_old_excited = 0
    elif id == 4:
        em = list(shy.keys())[emotion_var_old_shy]
        var = shy[em]
        emotion_var_old_shy+=1
        if (emotion_var_old_shy == len(shy)):
            emotion_var_old_shy = 0
    elif id == 5:
        em = list(sad.keys())[emotion_var_old_sad]
        var = sad[em]
        emotion_var_old_sad+=1
        if (emotion_var_old_sad == len(sad)):
            emotion_var_old_sad = 0

    l = []
    l.append(path + "emotion_game_2/" + em + "1.jpg")
    l.append(path + "emotion_game_2/" + em + "2.jpg")
    print("list is :", l)
    return l



has_redirected = False  # Add a global variable

@socketio.on('start game')
def start_game(message):
    global selected
    global speech_flag
    global speech_flag_emotion
    global game
    global has_redirected
    selected = 0
    speech_flag = False
    speech_flag_emotion = False
    print("message['who']: ",message['who'])
    if (message['who'] == 'start_game'):
        socketio.emit('redirect', {'url': url_for('first_view')}, room=request.sid)
        print("{'url': url_for('first_view')}")
        if (game == "emotion_game1" or game == "emotion_game2"):
            behaviorTalk_servc("Let's play a game")
        elif (game == "emotion_game3"):
            behaviorTalk_servc("Let's play a game, show me two emotion cards")
        elif (game == "action_game"):
            behaviorTalk_servc("Let's play a game")
        rospy.sleep(1)


@socketio.on('selected')  # when the user clicks the image on the tablet
def image_selected(message):
    global game
    global selected

    global emotion_game1_success, emotion_game2_success, emotion_game3_success
    global emotion_game1_failure, emotion_game2_failure, emotion_game3_failure

    next_dialogue = ["You can click next.", "Please press the next", "Let's go to next", "Let's move to next"]
    random_number = random.randint(0, 3)

    if (game == "emotion_game1"):
        global speech_flag_emotion
        global selected_emotion
        if not speech_flag_emotion:
            speech_flag_emotion = True
            print("emotion speak")
            rospy.sleep(1.0)
            if selected_emotion =="sad":
                selected_emotion = "saed"
            behaviorTalk_servc(selected_emotion)
            # rospy.sleep(1.0)
            behaviorTalk_servc(next_dialogue[random_number])
    elif (game == "emotion_game2"):
        global var
        if (selected == 0):
            if (message['who'] == "img00"):
                socketio.emit('highlight', var, broadcast=True)
                # emotion elaboration
                sentence = var
                print("sentence var: ",var)

                # speechSay_pub.publish(var)
                behaviorTalk_servc(var)
                rospy.sleep(1)
                selected = 1
                emotion_game2_success += 1
            else:
                speechSay_pub.publish("Please try again!")
                socketio.emit('emotion_repeat_update', "Please try again!", broadcast=True)
                emotion_game2_failure += 1
    elif (game == "action_game"):
        global speech_flag
        if not speech_flag:
            speech_flag = True
            talktext_pub.publish(action)
            rospy.sleep(1)
            # talktext_pub.publish(next_dialogue[random_number])
            # rospy.sleep(1)


@socketio.on('next button')
def next_button(message):
    global game
    global selected
    global speech_flag, speech_flag_emotion
    if (game == "emotion_game1"):
        rospy.sleep(2)
        talktext_pub.publish("Show me another emotion card!")
        global speech_flag_emotion
        if (speech_flag_emotion == True):
            speech_flag_emotion = False
            socketio.emit('update image', {'path': [path + "emotions/ask.jpg"]}, broadcast=True)


    elif (game == "emotion_game2"):
        rospy.sleep(2)
        talktext_pub.publish("Show me another emotion card!")
        rospy.sleep(1.5)
        if (selected == 1):
            selected = 0
            socketio.emit('update image', {'path': [path + "emotions/ask.jpg", path + "emotions/ask.jpg"]},
                          broadcast=True)
            socketio.emit('emotion_repeat_update', "Show me another emotion card!", broadcast=True)

    elif (game == "action_game"):
        rospy.sleep(2)
        talktext_pub.publish("Show me another action card!")
        global speech_flag
        if (speech_flag == True):
            speech_flag = False
            socketio.emit('update image', {'path': [path + "emotions/ask.jpg"]}, broadcast=True)


@app.route('/first_view')
def first_view():
    # # time.sleep(10)
    # print("game")
    # return render_template('emotion_game1.html')
    global game
    if (game == "emotion_game1"):  # first emotion game for young age
        return render_template('emotion_game1.html')
    elif (game == "emotion_game2"):  # second emotion game for old age
        print("here for old age")
        return render_template('emotion_game2.html')
    elif (game == "action_game"):
        return render_template('action_game.html')
    elif (game == "emotion_game3"):
        return render_template('emotion_game3.html')



######################################################################################### Main ############################################################################################

if __name__ == '__main__':
    threading.Thread(target=lambda: rospy.init_node('app',
                                                    disable_signals=True)).start()  # it helps to start the rospy and ends terminal
    speechSay_pub = rospy.Publisher('/qt_robot/speech/say', String, queue_size=10)
    talktext_pub = rospy.Publisher('/qt_robot/behavior/talkText', String, queue_size=10)
    gesturePlay_pub = rospy.Publisher('/qt_robot/gesture/play', String, queue_size=10)
    emotionShow_pub = rospy.Publisher('/qt_robot/emotion/show', String, queue_size=10)
    audioPlay_pub = rospy.Publisher('/qt_robot/audio/play', String, queue_size=10)

    speechStop_servc = rospy.ServiceProxy('/qt_robot/speech/stop', speech_stop)
    rospy.wait_for_service('/qt_robot/speech/stop')
    emotionStop_servc = rospy.ServiceProxy('/qt_robot/emotion/stop', emotion_stop)
    emotionStop_servc = rospy.ServiceProxy('/qt_robot/emotion/stop', emotion_stop)
    rospy.wait_for_service('/qt_robot/emotion/stop')
    gestureStop_servc = rospy.ServiceProxy('/qt_robot/gesture/stop', gesture_stop)
    rospy.wait_for_service('/qt_robot/gesture/stop')
    audioPlay_servc = rospy.ServiceProxy('/qt_robot/audio/stop', audio_stop)
    rospy.wait_for_service('/qt_robot/audio/play')
    speechSay_servc = rospy.ServiceProxy('/qt_robot/speech/say', speech_say)
    rospy.wait_for_service('/qt_robot/speech/say')
    behaviorTalk_servc = rospy.ServiceProxy('/qt_robot/behavior/talkText', behavior_talk_text)
    rospy.wait_for_service('/qt_robot/behavior/talkText')
    # speechConfig_servc = rospy.ServiceProxy('/qt_robot/speech/config', speech_config)
    # rospy.wait_for_service('/qt_robot/speech/config')
    gesturePlay_servc = rospy.ServiceProxy('/qt_robot/gesture/play', gesture_play)
    rospy.wait_for_service('/qt_robot/gesture/play')

    right_pub = rospy.Publisher('/qt_robot/right_arm_position/command', Float64MultiArray, queue_size=1)
    left_pub = rospy.Publisher('/qt_robot/left_arm_position/command', Float64MultiArray, queue_size=1)
    global f
    time_start = time.ctime()

    socketio.run(app, host='0.0.0.0', debug = True, use_reloader =False)  # connect to 192.168.100.2:5000 in web
    end = time.ctime()
