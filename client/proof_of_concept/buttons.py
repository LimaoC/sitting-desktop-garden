"""
File:
    sitting-desktop-garden/client/proof_of_concept/buttons.py

Purpose:
    Hardware test for the PiicoDev buttons.

Author:
    Gabriel Field (47484306)

Source:
    Largely based on https://core-electronics.com.au/guides/piicodev-button-getting-started-guide/#B62QRRH
"""

## SECTION: Imports

from PiicoDev_Switch import PiicoDev_Switch # Switch may be used for other types of PiicoDev Switch devices
from PiicoDev_Unified import sleep_ms



## SECTION: main()

def main():
    print("==== TEST: Chungus on one button ====")
    button = PiicoDev_Switch(double_press_duration = 400) # Double-presses are those that happen with interval <= 400ms
    basic_press_test(button)
    led_test(button)
    double_press_test(button)

    print("<?> Set button IDs to 0000 and 1110.")
    print("<?> Do this by setting switches down for '0' and up for '1'.")
    print("<?> You have 10 seconds...")
    sleep_ms(1000 * 10)
    print("<?> Assuming the button IDs have been set.")
    
    print("==== TEST: Chungi on two buttons ====")
    button0000 = PiicoDev_Switch(id = [0, 0, 0, 0])
    button1110 = PiicoDev_Switch(id = [1, 1, 1, 0])
    two_chungi(button0000, button1110)

    print("==== TEST: COMPLETE! ====")



## TEST: One-button

def basic_press_test(button):
    print("<?> BEGIN basic_press_test()")
    sleep_ms(2000)
    cycle = 0
    press_count = 0
    while cycle < 10:
        print("\tCycle: " + str(cycle))
        press_count += button.press_count
        print("\t\tWas pressed:       " + str(button.was_pressed))
        print("\t\tIs  pressed:       " + str(button.is_pressed))
        print("\t\tTotal press count: " + str(press_count))
        cycle += 1
        sleep_ms(1000)
    print("<?> END basic_press_test()")

def led_test(button):
    print("<?> BEGIN led_test()")
    sleep_ms(2000)
    cycle = 0
    button.led = False
    thinking_led = False
    while cycle < 10:
        print("\tCycle: " + str(cycle))
        button.led = not button.led
        thinking_led = False
        print("\tButton should be on: " + str(thinking_led))
        cycle += 1
        sleep_ms(1000)
    print("<?> END led_test()")

def double_press_test(button):
    print("<?> BEGIN double_press_test()")
    sleep_ms(2000)
    cycle = 0
    while cycle < 10:
        print("\tCycle: " + str(cycle))
        print("\tWas double-pressed: " + str(button.was_double_pressed))
        cycle += 1
        sleep_ms(1000)
    print("<?> END double_press_test()")



## TEST: Two buttons

def two_chungi(button0000, button1110):
    print("<?> BEGIN two_chungi()")
    sleep_ms(2000)
    cycle = 0
    button0000.press_count # Clear the count
    button1110.press_count # Clear the count
    while cycle < 10:
        print("\tCycle: " + str(cycle))
        print("\tButton with id 0000 pressed this many times since last time: " + str(button0000.press_count))
        print("\tButton with id 1110 pressed this many times since last time: " + str(button1110.press_count))
        cycle += 1
        sleep_ms(1000)
    print("<?> END two_chungi()")



## LAUNCH

if __name__ == "__main__":
    main()
