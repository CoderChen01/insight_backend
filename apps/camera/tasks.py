import base64
import datetime
import json
import time
from uuid import uuid4

import cv2
import requests
from celery import group, shared_task
from django.core.files.base import ContentFile
from incident.models import Incident
from interface.models import AISkill

from rest_tools.extract_frame_utils import NetworkCapture, is_opened
from rest_tools.redis_operations import RedisTaskQueue, RedisTaskState

from .models import Camera


def check_end(end_time):
    """
    check whether it is within the time period set by the user.
    :param end_time: the end time set by the user.
    :return: bool
    """
    now_time = datetime.datetime.now()
    now_time = datetime.time(now_time.hour, now_time.minute)
    return now_time >= end_time


def check_stopped(task_id):
    """
    check whether the user has paused the task
    :param task_id: the task id
    :return: bool
    """
    with RedisTaskState(task_id) as check_state:
        return check_state.check_stopped()


def clear_queue(task_id):
    """
    clear frame queue
    :param task_id: the task id
    :return: None
    """
    with RedisTaskQueue(task_id) as queue_clear:
        queue_clear.clear()


class Detect(object):
    """
    upload an image to server to detect something
    """

    def __init__(self, url, image):
        self.url = url
        self.image = image

    def get_result(self, faces=None):
        base_request = {"image": self.image}

        if faces:
            base_request.update(faces)

        response = requests.post(
            url=self.url,
            json=base_request,
            headers={"Content-Type": "application/json"},
        )
        response.encoding = "utf8"
        return response.json()


@shared_task(ignore_result=True)
def put_image(
    camera_url, coordinates, task_id, end_time_hour, end_time_minute
):
    cap = cv2.VideoCapture(camera_url)
    end_time = datetime.time(end_time_hour, end_time_minute)
    coordinates = json.loads(coordinates)
    username, camera_id = task_id.split("##")
    camera = Camera.objects.filter(
        user__username=username, camera_id=camera_id
    ).first()

    try:
        with RedisTaskQueue(task_id) as queue:
            while cap.isOpened():
                if check_end(end_time):
                    camera.state = 22
                    camera.save()
                    queue.clear()
                    cap.release()
                    return
                is_stopped = check_stopped(task_id)
                if is_stopped:
                    camera.state = is_stopped
                    camera.save()
                    queue.clear()
                    return

                retval, frame = cap.read()
                if not retval:
                    cap = cv2.VideoCapture(
                        camera_url
                    )  # if meet exception, restart connection
                    continue
                y_min = coordinates["y_min"]
                y_max = coordinates["y_max"]
                x_min = coordinates["x_min"]
                x_max = coordinates["x_max"]

                frame_cropped = frame[y_min:y_max, x_min:x_max]
                is_success, image = cv2.imencode(".png", frame_cropped)
                if is_success:
                    img = base64.b64encode(image.tobytes()).decode("utf8")
                else:
                    continue
                queue.put(
                    {
                        "image": img,
                        "current_time": datetime.datetime.now().__str__(),
                    }
                )
                for _ in range(10):
                    cap.grab()
    except Exception:
        with RedisTaskState(task_id=task_id) as task_state:
            task_state.set_state("error")
        clear_queue(task_id)


@shared_task(ignore_result=True)
def detect_image(
    skill_id,
    task_id,
    end_time_hour,
    end_time_minute,
    interval,
    faces=None,
    **info
):
    end_time = datetime.time(end_time_hour, end_time_minute)
    username, camera_id = task_id.split("##")
    camera = Camera.objects.filter(
        user__username=username, camera_id=camera_id
    ).first()
    ai_skill = AISkill.objects.filter(id=skill_id).first()
    skill_url = ai_skill.ai_skill_url
    ai_skill_retry_num = 3

    try:
        with RedisTaskQueue(task_id) as queue:
            while True:
                if check_end(end_time):
                    camera.state = 22
                    camera.save()
                    queue.clear()
                    return
                is_stopped = check_stopped(task_id)
                if is_stopped:
                    camera.state = is_stopped
                    camera.save()
                    queue.clear()
                    return

                start_time = time.time()
                image_item = queue.get()
                if not image_item:
                    continue
                image, current_time = image_item.get("image"), image_item.get(
                    "current_time"
                )

                try:
                    request_obj = Detect(url=skill_url, image=image)
                    if faces:
                        response = request_obj.get_result(faces=faces)
                    else:
                        response = request_obj.get_result()
                except requests.exceptions.ConnectionError:
                    if ai_skill_retry_num == 0:
                        ai_skill.state = 0
                        ai_skill.save()

                        camera.state = 20
                        camera.save()
                        queue.clear()
                        return
                    else:
                        ai_skill_retry_num = ai_skill_retry_num - 1
                        continue

                # if event occur, record result and image
                if response.get("has_event"):
                    # if response:
                    detected_image = ContentFile(
                        name=str(uuid4()) + ".png",
                        content=base64.b64decode(image),
                    )
                    Incident.objects.create(
                        user_id=info.get("user"),
                        incident_id=str(uuid4()),
                        camera_id=info.get("camera"),
                        ai_skill_id=info.get("ai_skill"),
                        incident_image=detected_image,
                        response=json.dumps(response),
                        occurrence_time=datetime.datetime.fromisoformat(
                            current_time
                        ),
                    )
                elapsed_time = time.time() - start_time
                if interval < elapsed_time:
                    continue
                time.sleep(interval - elapsed_time)  # extraction frequency
    except Exception:
        with RedisTaskState(task_id=task_id) as task_state:
            task_state.set_state("error")
        clear_queue(task_id)


@shared_task(ignore_result=True)
def dispatch_tasks(task_id, end_time_hour, end_time_minute):
    username, camera_id = task_id.split("##")
    camera = Camera.objects.filter(
        user__username=username, camera_id=camera_id
    ).first()  # get the camera model to extract frame

    ai_skill_settings = (
        camera.ai_skill_settings.all()
    )  # get all ai_skills setted
    for ai_skill_setting in ai_skill_settings:
        ai_skill = ai_skill_setting.ai_skill
        coordinates = ai_skill_setting.coordinates
        face_relevence = ai_skill_setting.face_relevance

        skill_url = ai_skill.ai_skill_url
        camera_url = camera.camera_url

        skill_test = None
        try:
            skill_test = requests.get(skill_url).status_code
            if skill_test != 200:
                ai_skill.state = 0
                ai_skill.save()
            else:
                ai_skill.state = 1
                ai_skill.save()
        except requests.exceptions.ConnectionError:
            ai_skill.state = 0
            ai_skill.save()

        camera_test = is_opened(camera_url=camera_url)
        if not camera_test:
            camera.state = 10  # connection failure
            camera.save()

        if skill_test == 200 and camera_test:
            info = {
                "user": camera.user.id,
                "camera": camera.id,
                "ai_skill": ai_skill.id,
            }

            all_faces = None
            if face_relevence:
                similarity = face_relevence.similarity
                quality = face_relevence.quality

                face_groups = face_relevence.face_group.all()
                face_images = []
                for face_group in face_groups:
                    faces = face_group.face_set.all()
                    if faces:
                        for face in faces:
                            face_image = face.face_image
                            face_images.append(
                                base64.b64encode(face_image.read())
                            )

                all_faces = {
                    "similarity": similarity,
                    "quality": quality,
                    "faces": face_images,
                }

            with RedisTaskState(task_id=task_id) as task_state:
                task_state.set_state("running")

            group(
                put_image.s(
                    camera_url=camera_url,
                    coordinates=coordinates,
                    task_id=task_id,
                    end_time_hour=end_time_hour,
                    end_time_minute=end_time_minute,
                ),
                detect_image.s(
                    skill_id=ai_skill.id,
                    task_id=task_id,
                    end_time_hour=end_time_hour,
                    end_time_minute=end_time_minute,
                    interval=camera.extraction_settings.frequency,
                    faces=all_faces,
                    **info
                ),
            ).apply_async()
        else:
            with RedisTaskState(task_id=task_id) as task_state:
                task_state.set_state("error")
            clear_queue(task_id)
