import os
import base64

import numpy
import cv2


class FaceDetection(object):
    def __init__(self, image):
        val_file = os.path.join(os.path.dirname(__file__), 'haarcascade_frontalface_default.xml')
        self.image = image
        self._haar_cascade_face = cv2.CascadeClassifier(val_file)

    @property
    def _base2cv2(self):
        img_string = base64.b64decode(self.image)
        np_array = numpy.frombuffer(img_string, numpy.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def detect(self):
        face_rects = self._haar_cascade_face.detectMultiScale(self._base2cv2, scaleFactor=1.2, minNeighbors=5)

        if len(face_rects) == 1:
            return True

        return False
