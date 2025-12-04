#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from ev3dev2.sound import Sound
from time import sleep
import time
import signal
import csv
import os
import datetime
sound = Sound()




threshold_black = 14
# Speed settings for motors (+ is forward, - is backward)
base_speed_right = -30
base_speed_left = base_speed_right-2
turn_speed_right = -100
turn_speed_left = turn_speed_right-2
turn_speed_absolute_right = -60
turn_speed_absolute_left = turn_speed_absolute_right -2
base_speed_left_uphill = -67
base_speed_right_uphill = -55
turn_speed_right_uphill = -75
turn_speed_left_uphill = turn_speed_right_uphill-10
search_speed_right = -18
search_speed_left = search_speed_right-2
forward_search_speed_right = -20
forward_search_speed_left = forward_search_speed_right-2
acceptance = 0
#positiv is down, negativ is up
base_speed_lift = 30
base_speed_lift_up = -80
base_speed_servo = 60


btn = ev3.Button()
Motor_left = ev3.LargeMotor('outA')
Motor_right = ev3.LargeMotor('outD')
Motor_servo = ev3.MediumMotor('outB')
Motor_lift = ev3.LargeMotor('outC')
color_sensor_left = ev3.ColorSensor('in1')
color_sensor_right = ev3.ColorSensor('in4')
ultrasonic_sensor = ev3.UltrasonicSensor('in3')
ultrasonic_sensor.mode = 'US-DIST-CM'
gyro_sensor = ev3.GyroSensor('in2')
gyro_sensor.mode = 'GYRO-ANG'

color_sensor_left.mode = 'COL-REFLECT'
color_sensor_right.mode = 'COL-REFLECT'
assert color_sensor_left.connected, "Left color sensor is not connected"
assert color_sensor_right.connected, "Right color sensor is not connected"
count = 0

Motor_left.run_direct()
Motor_right.run_direct()
Motor_lift.run_direct()
Motor_servo.run_direct()

def reset_gyro():
    if gyro_sensor.mode == 'GYRO-ANG':
        gyro_sensor.mode = 'GYRO-RATE'
        sleep(0.01)
        gyro_sensor.mode = 'GYRO-ANG'
        sleep(0.01)
    elif gyro_sensor.mode == 'GYRO-RATE':
        gyro_sensor.mode = 'GYRO-ANG'
        sleep(0.01)
        gyro_sensor.mode = 'GYRO-RATE'
        sleep(0.01)
def drive_forward_uphill():
    Motor_left.duty_cycle_sp = base_speed_left_uphill
    Motor_right.duty_cycle_sp = base_speed_right

def turn_right():
    l = color_sensor_left.reflected_light_intensity
    duty = int(turn_speed_left * (1.2 - (l / 100.0)))
    duty = max(-100, min(100, duty))
    Motor_left.duty_cycle_sp = duty
    Motor_right.duty_cycle_sp = abs(base_speed_right)+25
    reset_gyro()


def turn_left():
    l = color_sensor_right.reflected_light_intensity
    duty = int(turn_speed_right * (1.2 - (l / 100.0)))
    duty = max(-100, min(100, duty))
    Motor_right.duty_cycle_sp = duty
    Motor_left.duty_cycle_sp = abs(base_speed_left)+25
    reset_gyro()

def turn_right_absolute():
    start_time = time.time()
    Motor_left.duty_cycle_sp = turn_speed_absolute_right
    Motor_right.duty_cycle_sp = abs(turn_speed_absolute_left)
    while (start_time + 0.7) > time.time():
        if color_sensor_left.reflected_light_intensity < threshold_black:
            stop_motors()
            return 1,time.time() - start_time
    stop_motors()
    return 0,0

def turn_back_straight():
    start_time = time.time()
    Motor_left.duty_cycle_sp = turn_speed_absolute_right
    Motor_right.duty_cycle_sp = abs(turn_speed_absolute_left)
    while (start_time + 0.7) > time.time():
        pass
    stop_motors()

def turn_left_absolute():
    start_time = time.time()
    Motor_right.duty_cycle_sp = turn_speed_absolute_right
    Motor_left.duty_cycle_sp = abs(turn_speed_absolute_left)
    while (start_time + 0.7) > time.time():
        if color_sensor_right.reflected_light_intensity < threshold_black:
            stop_motors()
            return 1,time.time() - start_time
    stop_motors()
    return 0,0

def turn_left_180():
    start_time = time.time()
    Motor_right.duty_cycle_sp = turn_speed_absolute_right
    Motor_left.duty_cycle_sp = abs(turn_speed_absolute_left)
    while (start_time + 1.35) > time.time():
        pass    
    stop_motors()

def turn_right_uphill():
    l = color_sensor_left.reflected_light_intensity
    duty = int(turn_speed_left * (1 - (l / 100.0)))
    duty = max(-100, min(100, duty))
    Motor_left.duty_cycle_sp = duty
    #Motor_right.duty_cycle_sp = base_speed_right_uphill + 5
    Motor_right.duty_cycle_sp = abs(base_speed_left+20)

def turn_left_uphill():
    l = color_sensor_right.reflected_light_intensity
    duty = int(turn_speed_right * (1 - (l / 100.0)))
    duty = max(-100, min(100, duty))
    Motor_right.duty_cycle_sp = duty
    Motor_left.duty_cycle_sp = abs(base_speed_left+20)

def search_turn_right():
    Motor_left.duty_cycle_sp = search_speed_left
    Motor_right.duty_cycle_sp = abs(search_speed_right)

def search_turn_left():
    Motor_right.duty_cycle_sp = search_speed_right
    Motor_left.duty_cycle_sp = abs(search_speed_left)

def lift_up():
    Motor_lift.duty_cycle_sp = base_speed_lift_up
    sleep(1.5)
    Motor_lift.duty_cycle_sp = 0

def lift_down():
    Motor_lift.duty_cycle_sp = base_speed_lift
    sleep(1.5)
    Motor_lift.duty_cycle_sp = 0

def open_servo():
    Motor_servo.duty_cycle_sp = base_speed_servo
    sleep(3.3)
    Motor_servo.duty_cycle_sp = 0

def close_servo():
    Motor_servo.duty_cycle_sp = -base_speed_servo
    sleep(3.3)
    Motor_servo.duty_cycle_sp = 0

def stop_motors():
    Motor_left.duty_cycle_sp = 0
    Motor_right.duty_cycle_sp = 0

def move_forward():
    Motor_left.duty_cycle_sp = (base_speed_left)
    Motor_right.duty_cycle_sp = (base_speed_right)

def uphill_line_follow3():
    going_down = False
    count = 0
    while True:
        # use module-scope state variables
        #global left_latest, right_latest, count
        #print("Left:", color_sensor_left.reflected_light_intensity, " Right:", color_sensor_right.reflected_light_intensity )
        if gyro_sensor.mode != 'GYRO-RATE':
            gyro_sensor.mode = 'GYRO-RATE'
            sleep(0.01)
        
        if color_sensor_left.reflected_light_intensity - color_sensor_right.reflected_light_intensity > 6:
            turn_right_uphill()
            right_latest = True
        elif color_sensor_right.reflected_light_intensity - color_sensor_left.reflected_light_intensity > 6:
            turn_left_uphill()
            left_latest = True
        else:
            Motor_left.duty_cycle_sp = base_speed_left_uphill
            Motor_right.duty_cycle_sp = base_speed_right_uphill
        
        if gyro_sensor.rate < -10:
            going_down = True
        if going_down==True and (gyro_sensor.rate <= 1 and gyro_sensor.rate >= -1):
                count += 1
                if count > 4:
                    count = 0
                    break
        sleep(0.01)



def downhill_follow_the_line():
    while True:
        if gyro_sensor.mode != 'GYRO-RATE':
            gyro_sensor.mode = 'GYRO-RATE'
            sleep(0.01)
        
        if color_sensor_left.reflected_light_intensity - color_sensor_right.reflected_light_intensity > 6:
            #turn_right()
            print("TURN RIGHT")
        elif color_sensor_right.reflected_light_intensity - color_sensor_left.reflected_light_intensity > 6:
            #turn_left()
            print("TURN LEFT")
        else:
            Motor_left.duty_cycle_sp = abs(base_speed_left)+20
            Motor_right.duty_cycle_sp = abs(base_speed_right)+20
        
        if gyro_sensor.rate < -10:  
            going_down = True
        if going_down == True and (gyro_sensor.rate <= 1 and gyro_sensor.rate >= -1):
            count += 1
            if count > 4:
                count = 0
                break
    sleep(0.01)

def follow_the_line():
    if gyro_sensor.mode != 'GYRO-ANG':
        gyro_sensor.mode = 'GYRO-ANG'
        sleep(0.01)
    
    if color_sensor_left.reflected_light_intensity - color_sensor_right.reflected_light_intensity > 6:
        turn_right()
        return time.time()
    elif color_sensor_right.reflected_light_intensity - color_sensor_left.reflected_light_intensity > 6:
        turn_left()
        return time.time()
    else:
        Motor_left.duty_cycle_sp = base_speed_left
        Motor_right.duty_cycle_sp = base_speed_right
    

def scan_area(x,y):
    area_data = []
    search_turn_left()
    sleep(x)
    stop_motors()
    sleep(0.1)
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
    Motor_lift.run_direct()
    turn_left_180()
    open_servo()
    sleep(0.1)
    lift_down()
    area_data = scan_area(1*1.5,1.4*1.5)
    #print("Area data: ", area_data)
    #print(min(area_data),max(area_data))
    processed_threshold, acceptance_target = data_processing(data=area_data,precentage=0.35,acceptance_rate=0.08)
    #print("Threshold set to: ", processed_threshold)
    #print("Acceptance target set to: ", acceptance_target)
    intial_can_guess_movement(processed_threshold,acceptance_target)
    move_while_searching(grip_distance=5)
    close_servo()
    sleep(0.2)
    lift_up()
    sleep(0.2)
    Motor_lift.stop(stop_action='hold')
    move_forward()
    sleep(1.5)
    stop_motors()

def last_seen_black():
    if color_sensor_left.reflected_light_intensity < 30 or color_sensor_right.reflected_light_intensity < 30:
        current_time = time.time()
        return current_time
        
def check_if_line():
    var,time_ran = turn_left_absolute()
    if var == 1:
        return 1,time_ran,"left"
    turn_back_straight()
    var, time_ran = turn_right_absolute()
    if var == 1:
        return 1,time_ran,"right"
    turn_left_absolute()
    return 0,0,""

def calibrate():
    Motor_servo.duty_cycle_sp = -base_speed_servo
    sleep(0.2)
    Motor_servo.duty_cycle_sp = 0

        
def return_to_line(time_ran,direction):
    start_time = time.time()
    end_time = start_time + time_ran
    if direction == "left":
        Motor_right.duty_cycle_sp = abs(turn_speed_absolute_right)
        Motor_left.duty_cycle_sp = turn_speed_absolute_left
    else:
        Motor_left.duty_cycle_sp = turn_speed_absolute_left
        Motor_right.duty_cycle_sp = turn_speed_absolute_right
    while (end_time) > time.time():
        pass
    stop_motors()
    return 1

last_seen_black_time = time.time()

def competive_picker(): 
    global last_seen_black_time
    current_time = time.time()
    gyro_value = gyro_sensor.value()
    sleep(0.01)
    if gyro_value >10:
        uphill_line_follow3()
    if current_time - last_seen_black_time >= 1.5:
        var,time_ran,direction = check_if_line()
        if var == 0:
            search()
            sleep(0.01)
        else:
            return_to_line(time_ran,direction)
            last_seen_black_time = time.time()
    new_time = follow_the_line()
    if new_time is not None:
        last_seen_black_time = new_time


def main():
    var,time_ran,direction = check_if_line()
    if var == 0:
        sound.speak("did not find the line")
    if var == 1:
        sound.speak("found the line")
        return_to_line(time_ran,direction)

def init():
    lift_up()
    sleep(0.1)
    Motor_lift.stop(stop_action='hold')
    reset_gyro()
    return True

init_ran = False
#close_servo()

while True:
    if init_ran == False:
        init_ran = init()
    
    competive_picker()
    
    if btn.any():
        stop_motors()
        break

# # #

#open_servo()
# while True:
#     if btn.any():
#         calibrate()

