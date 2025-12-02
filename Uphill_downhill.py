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




threshold_left = 30
threshold_right = 350
# Speed settings for motors (+ is forward, - is backward)
base_speed_right = -30
base_speed_left = base_speed_right-2
turn_speed_right = -100
turn_speed_left = turn_speed_right-2
base_speed_left_uphill = -67
base_speed_right_uphill = -55
turn_speed_right_uphill = -75
turn_speed_left_uphill = turn_speed_right_uphill-10
color = ('unknown', 'black', 'blue', 'green', 'yellow', 'red', 'white', 'brown')

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

# --- CSV logger setup -------------------------------------------------
# Writes to the user's home directory so it works on the MindBrick
LOG_PATH = os.path.expanduser('~/sensor_log.csv')

def init_logger(path=LOG_PATH):
    try:
        needs_header = not os.path.exists(path)
        f = open(path, 'a', newline='')
        writer = csv.writer(f)
        if needs_header:
            writer.writerow(['timestamp', 'left_reflect', 'left_color', 'right_reflect', 'right_color'])
            f.flush()
        return f, writer
    except Exception as e:
        print('Could not open log file for writing:', e)
        return None, None

csv_file, csv_writer = init_logger()

def log_sensors():
    # Safe no-op if logging isn't available
    if not csv_writer or not csv_file:
        return
    ts = datetime.datetime.now().isoformat()
    try:
        l_ref = color_sensor_left.reflected_light_intensity
    except Exception:
        l_ref = ''
    try:
        r_ref = color_sensor_right.reflected_light_intensity
    except Exception:
        r_ref = ''

    csv_writer.writerow([ts, l_ref, r_ref,])
    try:
        csv_file.flush()
        try:
            os.fsync(csv_file.fileno())
        except Exception:
            # fsync may not be available or necessary; ignore errors
            pass
    except Exception:
        pass

# ----------------------------------------------------------------------


Motor_left.run_direct()
Motor_right.run_direct()



#Motor_left.duty_cycle_sp = base_speed_left
#Motor_right.duty_cycle_sp = base_speed_right
#left_latest = False
#right_latest = False



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

angle_list = []

def uphill_line_follow():
    if color_sensor_left.color != 2 and color_sensor_right.color != 2:
        #if left_latest:
            #Motor_right.duty_cycle_sp = turn_speed_right
        #elif right_latest:
            #Motor_left.duty_cycle_sp = turn_speed_left
            #Motor_left.duty_cycle_sp = turn_speed_left
            #Motor_right.duty_cycle_sp = turn_speed_right
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
        Motor_right.duty_cycle_sp = base_speed_right_uphill
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


#print("left:", color_sensor_left.reflected_light_intensity, " right:", color_sensor_right.reflected_light_intensity)




    # write sensor data to CSV on each cycle; non-blocking if logger unavailable
    #try:
    #    log_sensors()
    #except Exception:
    #    pass

# counter used when neither side has been detected recently
left_latest = False
right_latest = False
count = 0



def uphill_line_follow3():
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
    

def follow_the_line():
    if gyro_sensor.mode != 'GYRO-ANG':
        gyro_sensor.mode = 'GYRO-ANG'
        sleep(0.01)
    
    if color_sensor_left.reflected_light_intensity - color_sensor_right.reflected_light_intensity > 6:
        turn_right()
    elif color_sensor_right.reflected_light_intensity - color_sensor_left.reflected_light_intensity > 6:
        turn_left()
    else:
        Motor_left.duty_cycle_sp = base_speed_left
        Motor_right.duty_cycle_sp = base_speed_right



def downhill_follow_the_line():
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


def main():
    reset_gyro()
    count = 0
    while True:
    #print("Left:", color_sensor_left.reflected_light_intensity, " Right:", color_sensor_right.reflected_light_intensity )
        follow_the_line()
        #print("FTL", gyro_sensor.angle)
        going_down = False
        if gyro_sensor.angle > 18:
            while(True):
                uphill_line_follow3()
                #print("ULF", gyro_sensor.angle)
                #print("GD", going_down)
                if gyro_sensor.rate < -10:  
                    going_down = True
                if going_down == True and (gyro_sensor.rate <= 1 and gyro_sensor.rate >= -1):
                    count += 1
                    if count > 4:
                        count = 0
                        break
                sleep(0.01)
        sleep(0.01)



                    

            

#main()

while True:
    follow_the_line()
    going_up = False
    count = 0
    if gyro_sensor.angle > -18:
        while(True):
            downhill_follow_the_line()
            if gyro_sensor.rate > 10:
                going_up = True
            if going_up == True and (gyro_sensor.rate <= 1 and gyro_sensor.rate >= -1):
                count += 1
                if count > 4:
                    count = 0
                    break
            sleep(0.01)
    sleep(0.01)

