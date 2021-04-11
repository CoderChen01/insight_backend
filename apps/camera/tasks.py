import base64
import datetime
import time
import json
from uuid import uuid4

from celery import shared_task, group
import requests
import cv2
from django.core.files.base import ContentFile

from .models import Camera
from incident.models import Incident
from interface.models import AISkill
from rest_tools.extract_frame_utils import is_opened, NetworkCapture
from rest_tools.redis_operations import RedisTaskState, RedisTaskQueue


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
        base_request = {'image': self.image}

        if faces:
            base_request.update(faces)

        response = requests.post(
            url=self.url,
            json=base_request,
            headers={
                'Content-Type': 'application/json'
            })
        response.encoding = 'utf8'
        return response.json()


@shared_task(ignore_result=True)
def put_image(
        camera_url,
        coordinates,
        interval,
        task_id,
        end_time_hour,
        end_time_minute):
    """
    put images to redis
    :param camera_url: camera rtsp url
    :param coordinates: identifiable area
    :param interval: the interval of graping frame
    :param task_id: the task id
    :param end_time_hour: the hour of end time
    :param end_time_minute: the minute of end time
    :return: None
    """
    cap = NetworkCapture.create(camera_url)
    cap.start_read()
    end_time = datetime.time(end_time_hour, end_time_minute)
    coordinates = json.loads(coordinates)
    username, camera_id = task_id.split('##')
    camera = Camera.objects.filter(
        user__username=username,
        camera_id=camera_id
    ).first()

    try:
        while cap.is_started():
            with RedisTaskQueue(task_id) as queue:
                if check_end(end_time):
                    camera.state = 22
                    camera.save()
                    queue.clear()
                    cap.stop_read()
                    cap.release()
                    return
                if check_stopped(task_id):
                    camera.state = 22
                    camera.save()
                    queue.clear()
                    cap.stop_read()
                    cap.release()
                    return

                retval, frame = cap.read_latest_frame()
                if retval:
                    y_min = coordinates['y_min']
                    y_max = coordinates['y_max']
                    x_min = coordinates['x_min']
                    x_max = coordinates['x_max']

                    frame_cropped = frame[y_min:y_max, x_min:x_max]
                    is_success, image = cv2.imencode('.png', frame_cropped)
                    if is_success:
                        img = base64.b64encode(image.tobytes()).decode('utf8')
                    else:
                        continue
                    queue.put({
                        'image': img,
                        'current_time': datetime.datetime.now().__str__()
                    })
                else:
                    cap = NetworkCapture.create(camera_url)
                    cap.start_read()  # if meet exception, restart connection
                time.sleep(interval)  # extraction frequency
    except Exception:
        camera.state = 20
        camera.save()
        with RedisTaskState(task_id=task_id) as task_state:
            task_state.set_state('stopped')
        clear_queue(task_id)


@shared_task(ignore_result=True)
def detect_image(
        skill_id,
        task_id,
        end_time_hour,
        end_time_minute,
        faces=None,
        **info):
    end_time = datetime.time(end_time_hour, end_time_minute)
    username, camera_id = task_id.split('##')
    camera = Camera.objects.filter(
        user__username=username,
        camera_id=camera_id
    ).first()
    ai_skill = AISkill.objects.filter(id=skill_id).first()
    skill_url = ai_skill.ai_skill_url
    ai_skill_retry_num = 3

    try:
        while True:
            with RedisTaskQueue(task_id) as queue:
                if check_end(end_time):
                    camera.state = 22
                    camera.save()
                    queue.clear()
                    return
                if check_stopped(task_id):
                    camera.state = 22
                    camera.save()
                    queue.clear()
                    return

                image_item = queue.get()
                if not image_item:
                    continue
                image, current_time = image_item.get('image'), image_item.get('current_time')

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
                if response.get('has_event'):
                # if response:
                    detected_image = ContentFile(
                        name=str(uuid4()) + '.png',
                        content=base64.b64decode(image)
                    )
                    Incident.objects.create(
                        user_id=info.get('user'),
                        incident_id=str(uuid4()),
                        camera_id=info.get('camera'),
                        ai_skill_id=info.get('ai_skill'),
                        incident_image=detected_image,
                        response=json.dumps(response),
                        occurrence_time=datetime.datetime.fromisoformat(current_time)
                    )
    except Exception:
        camera.state = 20
        camera.save()
        with RedisTaskState(task_id=task_id) as task_state:
            task_state.set_state('stopped')
        clear_queue(task_id)


@shared_task(ignore_result=True)
def dispatch_tasks(task_id, end_time_hour, end_time_minute):
    username, camera_id = task_id.split('##')
    camera = Camera.objects.filter(
        user__username=username,
        camera_id=camera_id
    ).first()  # get the camera model to extract frame

    ai_skill_settings = camera.ai_skill_settings.all()  # get all ai_skills setted
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
                'user': camera.user.id,
                'camera': camera.id,
                'ai_skill': ai_skill.id
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
                            face_images.append(base64.b64encode(face_image.read()))

                all_faces = {
                    'similarity': similarity,
                    'quality': quality,
                    'faces': face_images
                }

            with RedisTaskState(task_id=task_id) as task_state:
                task_state.set_state('running')

            group(
                put_image.s(
                    camera_url=camera_url,
                    coordinates=coordinates,
                    interval=camera.extraction_settings.frequency,
                    task_id=task_id,
                    end_time_hour=end_time_hour,
                    end_time_minute=end_time_minute
                ),
                detect_image.s(
                    skill_id=ai_skill.id,
                    task_id=task_id,
                    end_time_hour=end_time_hour,
                    end_time_minute=end_time_minute,
                    faces=all_faces,
                    **info
                )
            ).apply_async()
        else:
            camera.state = 20
            camera.save()
            with RedisTaskState(task_id=task_id) as task_state:
                task_state.set_state('stopped')
            clear_queue(task_id)
