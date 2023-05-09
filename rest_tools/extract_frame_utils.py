import base64
import time
from threading import Event, Lock, Thread

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

    is_success, image = cv2.imencode(".png", preview)
    if not is_success:
        return False

    return base64.b64encode(image).decode("utf8")


class NetworkCapture(object):
    """Wrapper on OpenCV VideoCapture object.
    Args:
        camera_uri (str | int): uri of the used camera (see OpenCV doc for details)
        resolution (int, int): desired resolution for the grabbed frame (the resolution must be compatible with the driver)
    Instantiating this object will automatically start the polling of image in background.
    This wrapper is reponsible for automatically polling image on the camera.
    This ensures that we can always access the most recent image.
    """

    def __init__(self, camera_uri, resolution=(1920, 1080), lazy_setup=True):
        """Open video capture on the specified camera."""
        self.camera_uri = camera_uri
        self.resolution = resolution

        self._lock = None
        self.running = None
        self.cap = None
        self._t = None

        if not lazy_setup:
            self._setup()

    def _setup(self):
        self.cap = cv2.VideoCapture(self.camera_uri)

        if not self.cap.isOpened():
            raise Exception("not found camera...")

        self.cap.set(
            cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc("M", "J", "P", "G")
        )
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        self._lock = Lock()
        self.running = Event()

        self._img = None

        self._t = Thread(target=self._read_loop)
        self._t.daemon = True
        self._t.start()

        for _ in range(50):
            time.sleep(0.1)
            if self._img is not None:
                break

    def close(self):
        """Stop polling image and release the Video Capture."""
        if self.running is not None:
            self.running.clear()

        if self._t is not None:
            if self._t.is_alive():
                self._t.join()

        if self.cap is not None:
            self.cap.release()

    def _read_loop(self):
        self.running.set()

        while self.running.is_set():
            b, img = self.cap.read()

            if b:
                with self._lock:
                    self._img = img.copy()

    def read(self):
        """Retrieve the last grabbed image."""
        if not hasattr(self, "cap"):
            self._setup()

        with self._lock:
            return self._img is not None, self._img

    def __del__(self):
        self.close()
