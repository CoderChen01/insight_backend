import base64
from gevent import threading

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


class NetworkCapture(cv2.VideoCapture):
    def __init__(self, url):
        super().__init__(url)
        self.frame_receiver = None
        self._result = (None, None)
        self._reading = False

    @staticmethod
    def create(url):
        rtscap = NetworkCapture(url)
        rtscap.frame_receiver = threading.Thread(target=rtscap.recv_frame)
        rtscap.frame_receiver.daemon = True
        return rtscap

    def is_started(self):
        ok = self.isOpened()
        if ok and self._reading:
            ok = self.frame_receiver.is_alive()
        return ok

    def get_status(self):
        return self._reading

    def recv_frame(self):
        while self.isOpened():
            if not self._reading:
                return
            self._result = self.read()
        self._reading = False

    def read_latest_frame(self):
        return self._result

    def start_read(self):
        self._reading = True
        self.frame_receiver.start()

    def stop_read(self):
        self._reading = False
        if self.frame_receiver.is_alive():
            self.frame_receiver.join()
