import base64

import cv2


def is_opened(camera_url):
    cap = cv2.VideoCapture(camera_url)
    ret = cap.isOpened()
    cap.release()
    return ret


def get_preview(camera_url):
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        return False

    retval, preview = cap.read()
    if not retval:
        return False

    is_success, image = cv2.imencode('.png', preview)
    if not is_success:
        return False

    return base64.b64encode(image).decode('utf8')
