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
left_latest = False
right_latest = False

def turn_left():
    Motor_right.duty_cycle_sp = turn_speed_right
    Motor_left.duty_cycle_sp = abs(base_speed_left)


def turn_right():
    Motor_left.duty_cycle_sp = turn_speed_left
    Motor_right.duty_cycle_sp = abs(base_speed_right)


def reset_gyro():
    gyro_sensor.mode = 'GYRO-RATE'
    sleep(0.1)
    gyro_sensor.mode = 'GYRO-ANG'
    sleep(0.1)

angle_list = []

while True:
        if color_sensor_left.color != 2 and color_sensor_right.color != 2:
            if left_latest:
                Motor_right.duty_cycle_sp = turn_speed_right
            elif right_latest:
                Motor_left.duty_cycle_sp = turn_speed_left
            else:
                Motor_left.duty_cycle_sp = turn_speed_left
                Motor_right.duty_cycle_sp = turn_speed_right
                sleep(0.01)
        elif color_sensor_left.color != 2:
            turn_left()
            left_latest = True
            last_seen_time = time.time()
        elif color_sensor_right.color != 2:
            turn_right()
            right_latest = True
            last_seen_time = time.time()
        else:
            Motor_left.duty_cycle_sp = base_speed_left
            Motor_right.duty_cycle_sp = base_speed_right
            left_latest = False
            right_latest = False




#while True:
#    angle_list.append(gyro_sensor.angle)
#    if len(angle_list) > 30:
#        reset_gyro()
#        angle_list = []
#    print(gyro_sensor.angle)
#    sleep(0.1)