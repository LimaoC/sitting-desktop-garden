"""
File:
    sitting-desktop-garden/client/proof_of_concept/display.py

Purpose:
    Hardware test for the PiicoDev display.

Author:
    Gabriel Field (47484306)

Source:
    Largely based on https://core-electronics.com.au/guides/raspberry-pi/piicodev-oled-ssd1306-raspberry-pi-guide/

NOTE:
    Ensure that I2C is enabled on the RPi first!
"""

## SECTION: Imports

from PiicoDev_SSD1306 import *
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function
from math import sin, cos, pi
import random



## SECTION: main()

def main():
    display = create_PiicoDev_SSD1306()

    print("Screen width  is " + str(WIDTH))
    print("Screen height is " + str(HEIGHT))
    sleep_ms(2000)

    print("==== TEST: Basic functionality ====")
    draw_lines(display)
    draw_rectangles(display)

    print("==== TEST: Displaying text and images ====")
    draw_text(display)
    draw_images(display)

    print("==== TEST: Graph ====")
    draw_graph(display)

    print("==== TEST: COMPLETE! ====")
    


## TEST: Basic functionality

def draw_lines(display):
    print("<?> BEGIN draw_lines()")
    sleep_ms(2000)
    # Draw a line from (0, 0) to (WIDTH, HEIGHT)
    print("\tDrawing line from (0, 0) to (WIDTH, HEIGHT)")
    start_x = 0
    start_y = 0
    end_x = WIDTH
    end_y = HEIGHT
    colour = 1 # COLOURS: `0` for black or `1` for white
    display.line(start_x, start_y, end_x, end_y, colour) # Logically draw this line
    display.show() # Render all things logically drawn
    sleep_ms(5000)
    # Blank the screen
    print("\tBlanking the screen")
    display.fill(0) # Parameter is a COLOUR, either `0` for black or `1` for white.
    display.show()  # Render
    sleep_ms(1000)
    # Draw a funny thing
    print("\tDrawing a funny shape")
    points = [None] * 5
    for i in range(5):
        points[i] = ( WIDTH / 2  +  cos(2 * pi / 5 * i) * HEIGHT / 2 , # how tf do you continue a line again in python
                     HEIGHT / 2  +  sin(2 * pi / 5 * i) * HEIGHT / 2 )
    for i in range(5):
        display.line(points[i][0], points[i][1], points[(i + 2) % 5][0], points[(i + 2) % 5][1], 1)
        display.line(points[i][0], points[i][1], points[(i + 3) % 5][0], points[(i + 3) % 5][1], 1)
    display.show() # Render
    sleep_ms(5000)
    # Blank the screen
    print("\tBlanking the screen")
    display.fill(0)
    display.show()
    print("<?> END draw_lines()")

def draw_rectangles(display):
    print("<?> BEGIN draw_rectangles()")
    sleep_ms(2000)
    # Draw an unfilled rectangle
    print("\tDrawing an unfilled rectangle")
    start_x = 0
    start_y = 0
    end_x = WIDTH / 2
    end_y = HEIGHT / 2
    colour = 1 # white
    display.rect(start_x, start_y, end_x, end_y, colour) # UNFILLED rectangle
    display.show() # render
    sleep_ms(5000)
    # Blank screen
    print("\tBlanking the screen")
    display.fill(0)
    display.show()
    # Draw a filled rectangle
    print("\tDrawing a filled rectangle")
    display.fill_rect(start_x, start_y, end_x, end_y, colour) # FILLED rectangle
    display.show() # render
    sleep_ms(5000)
    # Blank the screen
    print("\tBlanking the screen")
    display.fill(0)
    display.show()
    print("<?> END draw_rectangles()")



## TEST: Text and images

def draw_text(display):
    print("<?> BEGIN draw_text()")
    sleep_ms(2000)

    # This should link to the font-pet-me-128.dat file in the current directory.
    # **I have no idea how to change the location where we store this file.**

    # Hello world
    print("\tDrawing hello world")
    text_to_display = "Hello, World!"
    top_left_x = 0
    top_left_y = 0
    colour = 1
    display.text(text_to_display, top_left_x, top_left_y, colour)
    display.show() # render
    sleep_ms(5000)
    # Long string
    print("\tDrawing long string")
    display.text("The quick brown fox jumped over the lazy dog", 0, 15, 1)
    display.show()
    sleep_ms(5000)
    # Blank screen
    print("\tBlanking screen")
    display.fill(0)
    display.show()
    sleep_ms(5000)
    # Goodbye world
    print("\tDrawing goodbye world")
    display.text("Goodbye, world T-T", 0, 0, 1)
    display.show()
    sleep_ms(5000)
    # Blank the screen
    print("\tBlanking the screen")
    display.fill(0)
    display.show()
    print("<?> END draw_text")

def draw_images(display):
    print("<?> BEGIN draw_images()")
    sleep_ms(2000)
    # Images are drawn from .pbm (Portable BitMap image) files.
    # They should have dimensions 128 x 64.

    # Draw PiicoDev logo
    print("\tDisplaying PiicoDev logo")
    colour = 1
    display.load_pbm("./resources/piicodev-logo.pbm", colour)
    display.show() # render
    sleep_ms(5000)
    # Blank screen
    print("\tBlanking screen")
    display.fill(0)
    display.show()
    sleep_ms(5000)
    # Draw hilarious image
    print("\tDisplaying hilarious image")
    display.load_pbm("./resources/hilarious.pbm", 1)
    display.show()
    sleep_ms(5000)
    # Blank screen
    print("\tBlanking screen")
    display.fill(0)
    display.show()
    print("<?> END draw_images()")



## TEST: Graph

def draw_graph(display):
    print("<?> BEGIN draw_graph()")
    sleep_ms(2000)
    
    curve = display.graph2D(minValue = -1, maxValue = -1, height = HEIGHT, width = WIDTH)
        # minValue= key is for the minimum value on the logical graph. This gets mapped into pixels automatically.
        # maxValue= key is for the maximum value on the logical graph. This gets mapped into pixels automatically.
        # height=   key is for maximum display height.
        # width=    key is for maximum display width.
    
    # Display a sine curve
    print("\tDisplaying a sine curve")
    for x in range(WIDTH):
        y_value = sin(2 * pi * x / WIDTH)
        display.fill(0) # NOTE: I don't know if this is necessary or not.
        display.updateGraph2D(curve, y_value) # Add to the graph
        display.show() # render
    sleep_ms(5000)
    # Add to the same curve
    print("\tAdding another period to that curve, slowly")
    for x in range(WIDTH):
        display.fill(0) # When you add to the curve, I reckon this will mean that the whole graph overwrites the previous one. Otherwise, you'd get white garbage all over the screen
        display.updateGraph2D(curve, sin(2 * pi * x / WIDTH)) # idk what this will do
        display.show()
        sleep_ms(100) # wait 1/10 of a second so that we can see what this does
    sleep_ms(5000)
    # Use a new curve to plot random values
    print("\tPlotting random values on a new curve, slowly")
    curve = display.graph2D(minValue = 0, maxValue = 1) # omitted height= and width= keys default to HEIGHT and WIDTH
    for _ in range(WIDTH * 2):
        display.fill(0)
        display.updateGraph2D(curve, random.random())
        display.show()
        sleep_ms(100)
    sleep_ms(5000)
    # Plot two curves simultaneously
    print("\tPlotting two curves simultaneously")
    linear = display.graph2D(minValue = 0, maxValue = WIDTH)
    sinusoidal = display.graph2D(minValue = -1, maxValue = -1)
    for x in range(WIDTH):
        display.fill(0)
        display.updateGraph2D(linear, x)
        display.updateGraph2D(sinusoidal, sin(2 * pi * x / WIDTH))
        display.show()
    sleep_ms(5000)
    # Blank display
    print("\tBlanking display")
    display.fill(0)
    display.show()
    print("<?> END draw_graph()")



## LAUNCH

if __name__ == "__main__":
    main()

