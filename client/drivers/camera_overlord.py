# This script periodically takes photos and saves them to
# a temporary file on ram. This allows multiple programs to
# access the camera feed at once.

from picamera2 import Picamera2
import os
import time

if __name__ == '__main__':
    picam2 = Picamera2()
    config = picam2.create_still_configuration({'size':(640,480)})
    picam2.configure(config)
    picam2.start()
    picam2.options['quality'] = 80

    try:
        f = open('/tmp/snapshot.jpg','x')
        f.close()
    except:
        print('Snapshot already exists')
        
    try:
        while True:
            picam2.capture_file("/tmp/snapshot2.jpg")
            os.replace("/tmp/snapshot2.jpg", "/tmp/snapshot.jpg")
            time.sleep(0.5)

    except KeyboardInterrupt:
        picam2.close()
        print('Closed nicely')
        quit()
