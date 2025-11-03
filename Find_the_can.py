#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from ev3dev2.sound import Sound
from time import sleep
import time
import signal

sound = Sound()




threshold_left = 30
threshold_right = 350
# Speed settings for motors (+ is forward, - is backward)
base_speed_right = -35
base_speed_left = base_speed_right-2
turn_speed_right = -90
turn_speed_left = turn_speed_right-2
search_speed_right = -18
search_speed_left = search_speed_right-2
forward_search_speed_right = -20
forward_search_speed_left = forward_search_speed_right-2
color = ('unknown', 'black', 'blue', 'green', 'yellow', 'red', 'white', 'brown')
#positv is open, negativ is close
base_speed_servo = 60
acceptance = 0
#positiv is down, negativ is up
base_speed_lift = 15
base_speed_lift_up = -80



btn = ev3.Button()
Motor_left = ev3.LargeMotor('outA')
Motor_right = ev3.LargeMotor('outC')
Motor_servo = ev3.MediumMotor('outB')
Motor_lift = ev3.LargeMotor('outD')
color_sensor_left = ev3.ColorSensor('in1')
color_sensor_right = ev3.ColorSensor('in4')
ultrasonic_sensor = ev3.UltrasonicSensor('in3')
ultrasonic_sensor.mode = 'US-DIST-CM'

color_sensor_left.mode = 'COL-REFLECT'
color_sensor_right.mode = 'COL-REFLECT'
assert color_sensor_left.connected, "Left color sensor is not connected"
assert color_sensor_right.connected, "Right color sensor is not connected"


Motor_left.run_direct()
Motor_right.run_direct()
Motor_servo.run_direct()
Motor_lift.run_direct()

#Motor_left.duty_cycle_sp = base_speed_left
#Motor_right.duty_cycle_sp = base_speed_right
left_latest = False
right_latest = False

def turn_left():
    Motor_right.duty_cycle_sp = turn_speed_right
    Motor_left.duty_cycle_sp = abs(base_speed_left)


def turn_right():
    Motor_left.duty_cycle_sp = turn_speed_left
    Motor_right.duty_cycle_sp = abs(base_speed_right)

def search_turn_right():
    Motor_left.duty_cycle_sp = search_speed_left
    Motor_right.duty_cycle_sp = abs(search_speed_right)

def search_turn_left():
    Motor_right.duty_cycle_sp = search_speed_right
    Motor_left.duty_cycle_sp = abs(search_speed_left)

def stop_motors():
    Motor_left.duty_cycle_sp = 0
    Motor_right.duty_cycle_sp = 0

def move_forward():
    Motor_left.duty_cycle_sp = (base_speed_left)
    Motor_right.duty_cycle_sp = (base_speed_right)

def lift_up():
    Motor_lift.duty_cycle_sp = base_speed_lift_up
    sleep(1.5)
    Motor_lift.duty_cycle_sp = 0

def lift_down():
    Motor_lift.duty_cycle_sp = base_speed_lift
    sleep(1.5)
    Motor_lift.duty_cycle_sp = 0

def follow_line():
    if color_sensor_left.color != 6 and color_sensor_right.color != 6:
        if left_latest:
            Motor_right.duty_cycle_sp = turn_speed_right
        elif right_latest:
            Motor_left.duty_cycle_sp = turn_speed_left
        else:
            Motor_left.duty_cycle_sp = turn_speed_left
            Motor_right.duty_cycle_sp = turn_speed_right
            sleep(0.01)
    elif color_sensor_left.color != 6:
        turn_left()
        left_latest = True
    elif color_sensor_right.color != 6:
        turn_right()
        right_latest = True
    else:
        Motor_left.duty_cycle_sp = base_speed_left
        Motor_right.duty_cycle_sp = base_speed_right
        left_latest = False
        right_latest = False

def open_close_servo():
    open_servo()
    sleep(0.5)
    close_servo()

def open_servo():
    Motor_servo.duty_cycle_sp = base_speed_servo
    sleep(3.4)
    Motor_servo.duty_cycle_sp = 0

def close_servo():
    Motor_servo.duty_cycle_sp = -base_speed_servo
    sleep(3.4)
    Motor_servo.duty_cycle_sp = 0


def scan_area(x,y):
    area_data = []
    search_turn_left()
    sleep(x)
    stop_motors()
    time_start = time.time()
    time_end = time.time()
    search_turn_right()
    while time_end - time_start < y:
        #value = ultrasonic_sensor.value()
        area_data.append(ultrasonic_sensor.value())
        time_end = time.time()
        sleep(0.01)
    stop_motors()
    return area_data

def bubblesort(data):
    n = len(data)
    for i in range(n-1):
        for j in range(n-i-1):
            if data[j] > data[j+1]:
                data[j], data[j+1] = data[j+1], data[j]
    return data

def data_processing(data,precentage,acceptance_rate):
    data = bubblesort(data)
    length = len(data)
    acceptance = int(acceptance_rate * length)
    print(length)
    percentage_take = int(precentage*length)
    threshold = data[percentage_take]
    return threshold, acceptance

def move_while_searching(grip_distance=5):
    while True:
        Motor_left.duty_cycle_sp = abs(forward_search_speed_left)
        Motor_right.duty_cycle_sp = abs(forward_search_speed_right)
        sleep(0.1)
        if ultrasonic_sensor.distance_centimeters < grip_distance:
            stop_motors()
            break

def intial_can_guess_movement(threshold,acceptance_target):
    global acceptance
    while True:
        search_turn_left()
        #print(ultrasonic_sensor.value())
        if ultrasonic_sensor.value() <= threshold:
            acceptance += 1
            if acceptance > acceptance_target:
                stop_motors()
                break
        else:
            acceptance = 0
        sleep(0.01)




def search():
    area_data = scan_area(1*1.5,1.8*1.5)
    print("Area data: ", area_data)
    print(min(area_data),max(area_data))
    processed_threshold, acceptance_target = data_processing(data=area_data,precentage=0.3,acceptance_rate=0.11)
    print("Threshold set to: ", processed_threshold)
    print("Acceptance target set to: ", acceptance_target)
    intial_can_guess_movement(processed_threshold,acceptance_target)
    move_while_searching(grip_distance=5)
    close_servo()
    sleep(0.2)
    lift_up()
    sleep(0.2)
    move_forward()
    sleep(1)
    stop_motors()

open_servo()
#lift_up()
#lift_down()
#search()
