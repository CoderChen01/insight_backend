import time
import json

from redis import Redis

from .conf import settings


class RedisClient:
    """
    Simply encapsulate the redis module
    """
    reids_url = None

    def __enter__(self):
        self.client = Redis.from_url(self.reids_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


class SaveEmailCaptchaMap(RedisClient):
    """
    Save the relationship between the captcha and the mailbox
    """
    reids_url = settings.EMAIL_CAPTCHA_MAP_CACHE

    def __init__(self, email, captcha):
        self.email = email
        self.captcha = captcha

    def save(self, key_name):
        current_timestamp = int(time.time())
        value = {
            'captcha': self.captcha,
            'add_timestamp': current_timestamp
        }
        self.client.hset(name=key_name, key=self.email, value=json.dumps(value))


class ValidateCaptcha(RedisClient):
    """
    validate captcha aoccording the email
    """
    reids_url = settings.EMAIL_CAPTCHA_MAP_CACHE

    def __init__(self, email, captcha):
        self.email = email
        self.captcha = captcha

    def validate(self, key_name):
        raw_value = self.client.hget(key_name, self.email)

        if raw_value is not None:
            value = json.loads(raw_value)
            current_timestamp = int(time.time())
            difference_timestamp = current_timestamp - value['add_timestamp']

            if self.captcha == value['captcha']:
                result = {
                    'result': '验证成功',
                    'flag': True
                }

                if difference_timestamp > 5 * 60:
                    result = {
                        'result': '验证码过期',
                        'flag': False
                    }

                return result

        return {
            'result': '验证码错误',
            'flag': False
        }


class RedisThrottleCache(RedisClient):
    """
    store user send mail rate
    """
    reids_url = settings.REDIS_THROTTLE_CACHE

    def __init__(self, key, value=None, expire=None):
        self.key = key
        self.value = value
        self.expire = expire

    def _set(self):
        if isinstance(self.value, list):
            self.value = json.dumps(self.value)

        self.client.set(name=self.key, value=self.value, ex=self.expire)

    def _get(self):
        raw_value = self.client.get(name=self.key)

        if raw_value:
            value = json.loads(raw_value)
            return value

        return []

    @classmethod
    def set(cls, key, history, duration):
        with cls(key=key, value=history, expire=duration) as set_obj:
            set_obj._set()

    @classmethod
    def get(cls, key, *args):
        with cls(key=key) as get_obj:
            return  get_obj._get()


class RedisTaskState(RedisClient):
    """store the task's state"""
    reids_url = settings.REDIS_CHECK_TASK_STATE

    def __init__(self, task_id):
        self.task_id = task_id

    def check_stopped(self):
        state = self.client.get(self.task_id)
        if state:
            if state.decode('utf8') == 'stopped':
                return True
        return False

    def set_state(self, state):
        self.client.set(self.task_id, state)


class RedisTaskQueue(RedisClient):
    """the image queue used by task"""
    reids_url = settings.REDIS_TASK_QUEUE

    def __init__(self, task_id):
        self.task_id = task_id

    def put(self, data):
        self.client.lpush(self.task_id, json.dumps(data))

    def get(self):
        data = self.client.rpop(self.task_id)
        if data:
            return json.loads(data)
        return


    def qsize(self):
        return self.client.llen(self.task_id)

    def clear(self):
        self.client.delete(self.task_id)
