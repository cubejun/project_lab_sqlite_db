from flask import Flask,render_template,url_for,request,redirect, make_response, jsonify
import random
import json
from time import time
from random import random
import threading
from sense_hat import SenseHat
import sqlite3
import random
import time

app = Flask(__name__)
sense = SenseHat()
sense.clear()
rotation_angle = 0

text_color = (255, 255, 255)  # White
bg_color = (0, 0, 0)  # Black

Y = (255, 255, 0)  # 노란색
O = (0, 0, 0)
# 스마일 이모지를 정의합니다.
smiley = [
    O, O, O, O, O, O, O, O,
    O, Y, Y, O, O, Y, Y, O,
    O, Y, Y, O, O, Y, Y, O,
    O, O, O, O, O, O, O, O,
    O, O, O, Y, Y, O, O, O,
    O, O, O, Y, Y, O, O, O,
    O, Y, O, O, O, O, Y, O,
    O, O, Y, Y, Y, Y, O, O,
]
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

screen_width = 8
screen_height = 8

snake_x = screen_width // 2
snake_y = screen_height // 2
snake_size = 1
snake_speed = 1
snake_x_change = 1
snake_y_change = 0

food_x = random.randint(0, screen_width - 1)
food_y = random.randint(0, screen_height - 1)

snake_body = [(snake_x, snake_y)]
running = False
high_score = 0

def initialize_game():
        global snake_x, snake_y, snake_size, snake_x_change, snake_y_change, food_x, food_y, snake_body, running
        snake_x = screen_width // 2
        snake_y = screen_height // 2
        snake_size = 1
        snake_x_change = 1
        snake_y_change = 0
        food_x = random.randint(0, screen_width - 1)
        food_y = random.randint(0, screen_height - 1)
        snake_body = [(snake_x, snake_y)]
        running = False  # 게임 종료 상태로 설정

        
def handle_joystick_event(event):
        print(f'Event: {event.action}, Direction: {event.direction}')
        global snake_x_change, snake_y_change, food_x, food_y
        if event.action == 'pressed':
            if event.direction == 'up' and snake_y_change == 0:
                snake_x_change = 0
                snake_y_change = -1
            elif event.direction == 'down' and snake_y_change == 0:
                snake_x_change = 0
                snake_y_change = 1
            elif event.direction == 'left' and snake_x_change == 0:
                snake_x_change = -1
                snake_y_change = 0
            elif event.direction == 'right' and snake_x_change == 0:
                snake_x_change = 1
                snake_y_change = 0
                
def generate_food():
    while True:
        new_food_x = random.randint(0, screen_width - 1)
        new_food_y = random.randint(0, screen_height - 1)
        if (new_food_x, new_food_y) not in snake_body:
            return new_food_x, new_food_y


def game_loop():
    global snake_x, snake_y, running, food_x, food_y,snake_size,snake_speed,snake_x_change,snake_x_change,snake_y_change
    
    while running:
        sense.stick.direction_any = handle_joystick_event
        snake_x += snake_x_change
        snake_y += snake_y_change

        if (snake_x, snake_y) in snake_body or snake_x < 0 or snake_x >= screen_width or snake_y < 0 or snake_y >= screen_height:
            sense.show_message("Game Over!", text_colour=red)
            initialize_game()
            sense.clear()
            #time.sleep(2)  # 2초 동안 대기
            continue  # 다시 게임 초기화로 이동
            
        snake_body.insert(0, (snake_x, snake_y))
        
        if snake_x == food_x and snake_y == food_y:
            food_x, food_y = generate_food()
            snake_size += 1
        if len(snake_body) > snake_size:
            snake_body.pop()

        sense.clear()
        for segment in snake_body:
            x, y = segment
            sense.set_pixel(x, y, 0, 0, 255)
        sense.set_pixel(food_x, food_y, 255, 0, 0)
        time.sleep(snake_speed)
    sense.clear()
        # sense.set_pixel(snake_x, snake_y, 0, 0, 255)  # 뱀은 파란색

        # time.sleep(snake_speed)
def update_score():
    global game_score, high_score
    game_score = snake_size
    # 최고 점수 업데이트
    if game_score > high_score:
        high_score = game_score
        
        
@app.route('/', methods=["GET", "POST"])
def main():
    return render_template('index.html')

# @app.route('/', methods=["GET", "POST"])
# def snake():
#     return render_template('snake.html')

@app.route('/data', methods=["GET", "POST"])
def data():
    # Data Format
    # [TIME, Temperature, Humidity]

    conn = sqlite3.connect('/home/cubejun/Desktop/New2/measurement_data.db')
    cursor = conn.cursor()
        
    cursor.execute("SELECT *FROM measurements")
    data = cursor.fetchall()
    
    temp_values = [item[2] for item in data]
    for  i in temp_values:
        temp = i
    humid_values = [item[1] for item in data]
    for  i in humid_values:
        humid = i
    x_values = [item[0] for item in data]
    for x in x_values:
        time = x
    
    
        
    data = [time*1000, temp, humid]

    response = make_response(json.dumps(data))

    response.content_type = 'application/json'
    return response

    
    

@app.route('/control', methods=['POST'])
def control():
    global rotation_angle

    action = request.form['action']
    if action == 'on':
        sense.show_message("EMBEDDED SYSTEM", text_colour=text_color, back_colour=bg_color) # LED 매트릭스를 녹색으로 설정
    elif action == 'batman':
        sense.set_pixels(smiley)  # LED 매트릭스를 끔
    elif action == 'rotate':
        rotation_angle += 90
        rotation_angle %= 360
        sense.set_rotation(rotation_angle)
        

    return render_template('index.html')

   
@app.route('/gyro_data')
def gyro_data():
    conn = sqlite3.connect('/home/cubejun/Desktop/New2/measurement_data.db')
    cursor = conn.cursor()
        
    cursor.execute("SELECT *FROM measurements")
    data = cursor.fetchall()
    gyro_x = [item[3] for item in data]
    for  i in gyro_x:
        x = i
    gyro_y = [item[4] for item in data]
    for  i in gyro_y:
        y = i
    gyro_z = [item[5] for item in data]
    for  i in gyro_z:
        z = i
    return jsonify({
        'x': x,
        'y': y,
        'z': z
    })

@app.route('/compass', methods=["GET"])
def sense_compass():
    mag = sense.get_compass()
    return jsonify({
            'heading': mag
        })

@app.route('/start_game', methods=['POST'])
def start_game():
    global snake_x, snake_y, snake_size, snake_x_change, snake_y_change, food_x, food_y, snake_body, running

    if request.method == 'POST' and not running:
        
        snake_x = screen_width // 2
        snake_y = screen_height // 2
        snake_size = 1
        snake_x_change = 1
        snake_y_change = 0
        food_x = random.randint(0, screen_width - 1)
        food_y = random.randint(0, screen_height - 1)
        snake_body = [(snake_x, snake_y)]
        running = True
        # 게임 루프 스레드 시작
        game_thread = threading.Thread(target=game_loop)
        game_thread.start()

    return jsonify({'message': 'Game started!'})
@app.route('/get_score')
def get_score():
    global high_score
    if snake_size > high_score:
        high_score = snake_size
    return jsonify({'score': snake_size, 'high_score': high_score})

@app.route('/stop_game', methods=['POST'])
def stop_game():
    global running
    running = False
    return jsonify({'message': 'Game stopped!'})

@app.route('/get_led_matrix', methods=['GET'])
def get_led_matrix():
    led_matrix = []
    for y in range(8):
        row = []
        for x in range(8):
            pixel = sense.get_pixel(x, y)
            row.append(pixel)
        led_matrix.append(row)
    
    return jsonify({'matrix': led_matrix})

if __name__ == "__main__":
    sense.stick.direction_any = handle_joystick_event
    app.run(host='0.0.0.0', debug=True)
