#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from ev3dev2.sound import Sound
from time import sleep
import time
import signal
sound = Sound()
#sound.speak("Drive")

threshold_left = 30
threshold_right = 350
# Speed settings for motors (+ is forward, - is backward)
base_speed_right = -35
base_speed_left = base_speed_right-2
turn_speed_right = -90
turn_speed_left = turn_speed_right-2
color = ('unknown', 'black', 'blue', 'green', 'yellow', 'red', 'white', 'brown')
last_seen_time = None



btn = ev3.Button()
Motor_left = ev3.LargeMotor('outA')
Motor_right = ev3.LargeMotor('outB')
color_sensor_left = ev3.ColorSensor('in1')
color_sensor_right = ev3.ColorSensor('in2')


color_sensor_left.mode = 'COL-REFLECT'
color_sensor_right.mode = 'COL-REFLECT'
assert color_sensor_left.connected, "Left color sensor is not connected"
assert color_sensor_right.connected, "Right color sensor is not connected"


Motor_left.run_direct()
Motor_right.run_direct()


Motor_left.duty_cycle_sp = base_speed_left
Motor_right.duty_cycle_sp = base_speed_right
left_latest = False
right_latest = False

def turn_left():
    Motor_right.duty_cycle_sp = turn_speed_right
    Motor_left.duty_cycle_sp = abs(base_speed_left)


def turn_right():
    Motor_left.duty_cycle_sp = turn_speed_left
    Motor_right.duty_cycle_sp = abs(base_speed_right)

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
        last_seen_time = time.time()
        return last_seen_time
    elif color_sensor_right.color != 6:
        turn_right()
        right_latest = True
        last_seen_time = time.time()
        return last_seen_time
    else:
        Motor_left.duty_cycle_sp = base_speed_left
        Motor_right.duty_cycle_sp = base_speed_right
        left_latest = False
        right_latest = False

def timer_to_enable_search(timeout=5,last_seen_time=None):
    if last_seen_time is None:
        last_seen_time = time.time()
    enable_search = (time.time() - last_seen_time) > timeout
    return enable_search, last_seen_time

def search():
    Motor_left.duty_cycle_sp = turn_speed_left
    Motor_right.duty_cycle_sp = abs(base_speed_right)
    sleep(0.3)
    Motor_left.duty_cycle_sp = abs(base_speed_left)
    Motor_right.duty_cycle_sp = turn_speed_right
    sleep(0.6)
    Motor_left.duty_cycle_sp = turn_speed_left
    Motor_right.duty_cycle_sp = abs(base_speed_right)
    sleep(0.3)

def rescue():
    if touch_sensor.is_pressed:
        sound.speak("Rescue")
        Motor_left.duty_cycle_sp = -base_speed_left
        Motor_right.duty_cycle_sp = -base_speed_right
        sleep(1)
        Motor_left.duty_cycle_sp = turn_speed_left
        Motor_right.duty_cycle_sp = abs(base_speed_right)
        sleep(0.5)

def return_to_line():
    while color_sensor_left.color != 6 and color_sensor_right.color != 6:
        Motor_left.duty_cycle_sp = turn_speed_left
        Motor_right.duty_cycle_sp = abs(base_speed_right)
    Motor_left.duty_cycle_sp = base_speed_left
    Motor_right.duty_cycle_sp = base_speed_right


def main():
    while True:
            if btn.any():
                Motor_left.duty_cycle_sp = 0
                Motor_right.duty_cycle_sp = 0
                sound.speak("Stop")
                break
            enable_search, last_seen_time = timer_to_enable_search(last_seen_time=last_seen_time)
            last_seen_time = follow_line()
            #while gyro_sensor.value() > 1:
            #    down_hill_follow_line()
            while enable_search:
                search()
                rescue()
                return_to_line()
                enable_search = False

