#!/usr/bin/env python3

from ev3dev2.motor import *
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.button import Button # Import the Button class
from ev3dev2.power import PowerSupply # Import the PowerSupply class
from ev3dev2.sensor.lego import TouchSensor
import time
from time import sleep


m_l = LargeMotor('outA')

m_r = LargeMotor('outD')


cl_l = ColorSensor('in1')

cl_r = ColorSensor('in4')

touch_sensor = TouchSensor('in2') # Or whichever port you use

cl_l.mode = 'COL-REFLECT'

cl_r.mode = 'COL-REFLECT'

mod = 1

# black = 0, white = 100


#ultra = UltrasonicSensor('in1')

#ultra.mode = 'US-DIST-CM'

btn = Button()

power = PowerSupply()


def linefollow():

    motor_speed = -20

    timer_stop = 175


    battery_start = power.measured_volts

    time_start = time.time()


    # PID vars

    Kp = 2.45 #2.45*5 #2.45*4 #2.45*3 #2.45*2 #2.45

    Ki = 0#0#0

    Kd = 1.05*5 #1.05*3 #1.05*2#1.05


    dt = 0.01

    integral = 0

    dif_old = 0


    m_l_input = 0

    m_r_input = 0


    isRunning = True

    white_counter = 0


    while isRunning:

        # Read sensors

        reflect_l = cl_l.value()

        reflect_r = cl_r.value()

        # print("L:", reflect_l, " R:", reflect_r)


        #ultra_dist = ultra.distance_centimeters


        #--------------touch sensor--------------#

        if touch_sensor.is_pressed:

            total_time = time.time() - time_start

            print("total time to goal", total_time)

            battery_end = battery_start - power.measured_volts

            print("battery level lost", battery_end) #

            isRunning = False



        # ----- PID -----

        dif = reflect_r - reflect_l


        # Product

        p_out = dif * Kp


        # Integral

        integral += dif * dt

        i_out = Ki * integral


        # Derivative

        derivative = dif - dif_old

        d_out = Kd * derivative


        # Total

        output = p_out + i_out + d_out


        dif_old = dif # update old


        # print(output)

        output = -output


        # ------------------

        # Motor control stuff




        # m_l_input = (motor_speed * mod - output)

        # m_r_input = (motor_speed * mod + output)

        m_l_input = (motor_speed - output) * mod

        m_r_input = (motor_speed + output) * mod


        # Limit motor speed -> So it cannot react to hard

        limit = min(abs(2.5 * motor_speed), 100)


        if m_l_input < -limit:

            m_l_input = -limit

        if m_l_input > limit:

            m_l_input = limit

        if m_r_input < -limit:

            m_r_input = -limit

        if m_r_input > limit:

            m_r_input = limit

        # ------------------

        # Steer motor

        m_l.on(m_l_input)

        m_r.on(m_r_input)


        sleep(dt)

    #return 1



def main():

# Wait for button press

    while not btn.any():

        m_l.on(0)

        m_r.on(0)

        sleep(0.05)

    linefollow()


while True:
    main() 