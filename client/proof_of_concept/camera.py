"""
File:
    sitting-desktop-garden/client/proof_of_concept/buttons.py

Purpose:
    Hardware test for the PiicoDev buttons.

Author:
    Gabriel Field (47484306)

Source:
    Largely based on https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0
"""

## SECTION: Imports

from picamera2 import Picamera2, Preview
from PiicoDev_Unified import sleep_ms
from time import time



## SECTION: main()

def main():
    print("==== TEST: Preview ====")
    picam2 = Picamera2()
    test_preview(picam2)

    print("==== TEST: Pics ====")
    test_pics(picam2)

    print("==== TEST: Vids ====")
    test_vids(picam2)

    print("==== TEST: COMPLETE! ====")



## TEST: Preview

def test_preview(picam2):
    print("<?> BEGIN test_preview()")
    sleep_ms(2000)
    # Preview for 10 seconds
    print("\tStarting preview for 10 seconds... Requires monitor!!")
    picam2.start_preview(Preview.QTGL)
    picam2.start()
    sleep_ms(10000)
    picam2.close()
    print("<?> END test_preview()")



## TEST: Pics

def test_pics(picam2):
    print("<?> BEGIN test_pics()")
    sleep_ms(2000)
    # Take a single picture
    print("\tTaking a picture to ./camera_dump/picture-00.jpg")
    start = time()
    picam2.start_and_capture_file("./camera_dump/picture-00.jpg")
    picam2.close()
    end = time()
    print("\t\t^done. Took " + str(end - start) + " seconds")
    sleep_ms(5000)
    # Take many pictures
    print("\tTaking 10 pictures to ./camera_dump-pictures-?.jpg for ? = 0 .. 9, with delay 0.1 seconds")
    start = time()
    picam2.start_and_capture_files("./camera_dump/pictures-{:d}.jpg", num_files = 10, delay = 0.1)
    picam2.close()
    end = time()
    print("\t\t^done. Took " + str(end - start) + " seconds")
    sleep_ms(5000)
    print("<?> END test_pics()")



## TEST: Vids

def test_vids(picam2):
    print("<?> BEGIN test_vids()")
    sleep_ms(2000)
    # Take a single video for 10 seconds
    print("\tTaking a 10-second video to ./camera_dump/video-00.jpg")
    start = time()
    picam2.start_and_record_video("./camera_dump/video-00.jpg", duration = 10, show_preview = False)
    picam2.close()
    end = time()
    print("\t\t^done. Took " + str(end - start) + " seconds")
    sleep_ms(5000)
    # Taking many short videos
    print("\tTaking ten 1-second videos to ./camera_dump/shorts-?.jpg for ? = 0 .. 9")
    start = time()
    for i in range(10):
        picam2.start_and_record_video("./camera_dump/shorts-" + str(i) + ".jpg", duration = 1, show_preview = False)
        picam2.close()
    end = time()
    print("\t\t^done. Took " + str(end - start) + " seconds")
    # Taking many tiny videos
    start = time()
    for i in range(100):
        print("\tTaking 100 0.1-second videos to ./camera_dump/tiny-%02f" % i, duration = 0.1, show_preview = False)
        picam2.close()
    end = time()
    print("\t\t^done. Took " + str(end - start) + " seconds")
    sleep_ms(5000)
    # Take many short videos without .close()
    print("\t Taking ten 1-second videos without .close() to ./camera_dump/open-?.jpg for ? = 0 .. 9")
    start = time()
    for i in range(10):
        picam2.start_and_record_video("./camera_dump/open-" + str(i) + ".jpg", duration = 1, show_preview = False)
    picam2.close()
    end = time()
    print("\t\t^done. Took " + str(end - start) + " seconds")
    sleep_ms(5000)
    print("<?> END test_vids()")



## LAUNCH

if __name__ == "__main__":
    main()
