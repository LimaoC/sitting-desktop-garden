"""
File:
    sitting-desktop-garden/client/proof_of_concept/servo_driver.py

Purpose:
    Hardware test for the PiicoDev servos and server driver.

Author:
    Gabriel Field (47484306)

Source:
    Largely based on https://core-electronics.com.au/guides/piicodev/piicodev-servo-driver-pca9685-getting-started-guide/#JEFNE3E
"""

## SECTION: Imports

from PiicoDev_Servo import PiicoDev_Servo, PiicoDev_Servo_Driver
from PiicoDev_Unified import sleep_ms
from math import sin, pi



## SECTION: main()

def main():
    print("==== TEST: Basic use ====")
    controller = PiicoDev_Servo_Driver() # Initialise the Servo Driver Module
    servo = PiicoDev_Servo(controller, 1) # Simple setup: Attach a servo to channel 1 of the controller with default properties
    test_step(servo)
    continuous_servo = PiicoDev_Servo(controller, 1, midpoint_us=1500, range_us=1800) # Connect a 360° servo to channel 2
    test_spinny(continuous_servo)

    print("<?> Hook up two servos, with channels 1 and 2")
    print("<?> You have 10 seconds")
    sleep_ms(10000)
    print("<?> Assuming they're allg")

    print("==== TEST: Multiple servos ====")


    print("==== TEST: COMPLETE! ====")
    servo1 = PiicoDev_Servo(controller, 1)
    servo2 = PiicoDev_Servo(controller, 2)
    test_multiple(servo1, servo2)


## TEST: Basic use

def test_step(servo):
    print("<?> BEGIN test_step()")
    sleep_ms(2000)
    print("\tStepping the servo")
    servo.angle = 0
    sleep_ms(1000)
    servo.angle = 90
    print("<?> END test_step()")

def test_spinny(continuous_servo):
    print("<?> BEGIN test_spinny()")
    sleep_ms(2000)
    print("\tStopping")
    continuous_servo.speed = 0
    sleep_ms(5000)
    print("\tGoing full-speed forwards")
    continuous_servo.speed = 1
    sleep_ms(5000)
    print("\tGoing half-speed forwards")
    continuous_servo.speed = 0.5
    sleep_ms(5000)
    print("\tGoing half-speed backwards")
    continuous_servo.speed = -0.5
    sleep_ms(5000)
    print("\tGoing full-speed backwards")
    continuous_servo.speed = -1
    sleep_ms(5000)
    print("\tStopping")
    continuous_servo.speed = 0
    sleep_ms(5000)
    print("<?> END test_spinny()")



## TEST: Multiple servos

def test_multiple(servo1, servo2):
    print("<?> BEGIN test_multiple()")
    sleep_ms(2000)
    # This takes 18 seconds
    for i in range(1800):
        servo1.angle = 90 + 90 * sin(i * 2 * pi / 1800)
        servo2.angle = 90 - 90 * sin(i * 2 * pi / 1800)
        sleep_ms(10)
    print("<?> END test_multiple()")




## LAUNCH

if __name__ == "__main__":
    main()
