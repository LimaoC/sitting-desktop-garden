from pprint import pprint
import cv2
from deepface import DeepFace


ENTER_ASCII = 13


def take_photo(photo_name):
    capture = cv2.VideoCapture(0)
    while True:
        success, frame = capture.read()
        if not success:
            continue

        cv2.imshow(f"Camera Preview for {photo_name}: Press enter to take photo", frame)

        if cv2.waitKey(1) & 0xFF == ENTER_ASCII:
            cv2.imwrite(photo_name, frame)

            break

    capture.release()
    cv2.destroyAllWindows()


# Take two photos. Press enter to confirm photo.
print("Please take two photos")
take_photo("photo1.png")
take_photo("photo2.png")


# Verify that photos are of same person.
print("Deepface output")
pprint(DeepFace.verify("photo1.png", "photo2.png", model_name="GhostFaceNet"))
