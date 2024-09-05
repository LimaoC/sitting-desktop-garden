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
from PiicoDev_Unified import sleep_ms



## SECTION: main()

def main():
    print("<!> BEGIN main()...")
    GPIO.setmode(GPIO.BOARD) # use P1 header pin numbering convention

    # Set data directions
    GPIO.setup(17, GPIO.IN)
    GPIO.setup(18, GPIO.OUT)

    print("<?> Will read from pin 17 into code; will write to pin 18.")
    print("<!> Doing that in 5 seconds...")
    sleep_ms(5000)

    input_value = GPIO.input(17)
    print("<!> Read " + str(input_value) + " from pin 17")
    GPIO.output(18, GPIO.HIGH)
    print("<!> Wrote high to pin 18")
    
    print("<?> Writing low to pin 18 in 2 seconds")
    sleep_ms(2000)
    GPIO.output(18, GPIO.LOW)

    print("<!> END main()")



## LAUNCH

if __name__ == "__main__":
    main()

