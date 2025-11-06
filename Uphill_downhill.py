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
turn_speed_right = -100
turn_speed_left = turn_speed_right-2
base_speed_left_uphill = -47
turn_speed_right_uphill = -75
turn_speed_left_uphill = turn_speed_right_uphill-10
color = ('unknown', 'black', 'blue', 'green', 'yellow', 'red', 'white', 'brown')

btn = ev3.Button()
Motor_left = ev3.LargeMotor('outA')
Motor_right = ev3.LargeMotor('outC')
Motor_servo = ev3.MediumMotor('outB')
Motor_lift = ev3.LargeMotor('outD')
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


Motor_left.run_direct()
Motor_right.run_direct()



#Motor_left.duty_cycle_sp = base_speed_left
#Motor_right.duty_cycle_sp = base_speed_right
#left_latest = False
#right_latest = False

def drive_forward_uphill():
    Motor_left.duty_cycle_sp = base_speed_left_uphill
    Motor_right.duty_cycle_sp = base_speed_right

def turn_left():
    Motor_right.duty_cycle_sp = turn_speed_right
    Motor_left.duty_cycle_sp = abs(base_speed_left)

def turn_right():
    Motor_left.duty_cycle_sp = turn_speed_left
    Motor_right.duty_cycle_sp = abs(base_speed_right)

def turn_right2():
    Motor_left.duty_cycle_sp = turn_speed_left*(1.2-(color_sensor_left.reflected_light_intensity/100))
    Motor_right.duty_cycle_sp = abs(base_speed_right)+20
    
def turn_left2():
    Motor_right.duty_cycle_sp = turn_speed_right*(1.2-(color_sensor_right.reflected_light_intensity/100))
    Motor_left.duty_cycle_sp = abs(base_speed_left)+20

def turn_right_uphill():
    Motor_left.duty_cycle_sp =  turn_speed_left_uphill
    Motor_right.duty_cycle_sp = base_speed_right+20

def turn_left_uphill():
    Motor_right.duty_cycle_sp = turn_speed_right_uphill
    Motor_left.duty_cycle_sp = base_speed_left_uphill+20

def reset_gyro():
    gyro_sensor.mode = 'GYRO-RATE'
    sleep(0.1)
    gyro_sensor.mode = 'GYRO-ANG'
    sleep(0.1)

angle_list = []

def uphill_line_follow():
    if color_sensor_left.color != 2 and color_sensor_right.color != 2:
        #if left_latest:
            #Motor_right.duty_cycle_sp = turn_speed_right
        #elif right_latest:
            #Motor_left.duty_cycle_sp = turn_speed_left
            Motor_left.duty_cycle_sp = turn_speed_left
            Motor_right.duty_cycle_sp = turn_speed_right
            sleep(0.01)
    elif color_sensor_left.color != 2:
        turn_left_uphill()
        #left_latest = True
        last_seen_time = time.time()
    elif color_sensor_right.color != 2:
        turn_right_uphill()
        #right_latest = True
        last_seen_time = time.time()
    else:
        Motor_left.duty_cycle_sp = base_speed_left_uphill
        Motor_right.duty_cycle_sp = base_speed_right
        #left_latest = False
        #right_latest = False



def uphill_line_follow2():
    time_start = time.time()
    time_end = 0.1
    if color_sensor_left.color != 2:
        while(time.time() - time_start < time_end):
            turn_left_uphill()
            sleep(0.01)
        Motor_left.duty_cycle_sp = base_speed_left_uphill
        Motor_right.duty_cycle_sp = base_speed_right
    elif color_sensor_right.color != 2:
        while(time.time() - time_start < time_end):
            turn_right_uphill()
            sleep(0.01)
        Motor_left.duty_cycle_sp = base_speed_left_uphill
        Motor_right.duty_cycle_sp = base_speed_right
    else:
        Motor_left.duty_cycle_sp = base_speed_left_uphill
        Motor_right.duty_cycle_sp = base_speed_right
        #left_latest = False
        #right_latest = False


def follow_the_line():
    if color_sensor_left.reflected_light_intensity - color_sensor_right.reflected_light_intensity > 6:
        turn_right2()
    elif color_sensor_right.reflected_light_intensity - color_sensor_left.reflected_light_intensity > 6:
        turn_left2()
    else:
        Motor_left.duty_cycle_sp = base_speed_left
        Motor_right.duty_cycle_sp = base_speed_right


while True:
    follow_the_line()





#while True:
#    angle_list.append(gyro_sensor.angle)
#    if len(angle_list) > 30:
#        reset_gyro()
#        angle_list = []
#    print(gyro_sensor.angle)
#    sleep(0.1)