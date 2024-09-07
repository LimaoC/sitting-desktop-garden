"""
File:
    sitting-desktop-garden/client/proof_of_concept/gpio.py

Purpose:
    Hardware test for the GPIO pins, interfacing through RPi.GPIO.

Author:
    Gabriel Field (47484306)

Source:
    Largely based on https://elinux.org/RPi_GPIO_Code_Samples#RPi.GPIO
    See also https://elinux.org/RPi_Low-level_peripherals#General_Purpose_Input.2FOutput_.28GPIO.29
"""

## SECTION: Imports

import RPi.GPIO as GPIO # WARNING: This should be installed by default on the RPi, 
                        # but not on your local machine. 
                        #  I haven't `poetry add`ed it (I tried, but it failed >:( ).
#from PiicoDev_Unified import sleep_ms
from time import sleep



## SECTION: main()

def main():
    print("<!> BEGIN main()...")
    GPIO.setmode(GPIO.BCM) # use pin numbering convention as per the PiicoDev header

    # Set data directions
    GPIO.setup(7, GPIO.IN)
    GPIO.setup(8, GPIO.OUT)

    print("<?> Will read from pin 7 into code; will write to pin 8.")
    print("<!> Doing that in 5 seconds...")
    sleep(5)

    input_value = GPIO.input(7)
    print("<!> Read " + str(input_value) + " from pin 7")
    GPIO.output(8, GPIO.HIGH)
    print("<!> Wrote high to pin 8")
    
    print("<?> Writing low to pin 8 in 2 seconds")
    sleep(2)
    GPIO.output(8, GPIO.LOW)

    print("<!> END main()")



## LAUNCH

if __name__ == "__main__":
    main()

