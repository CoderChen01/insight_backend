from django.conf import settings as config


class Settings:
    """
    Encapsulate custom settings
    """
    @property
    def EMAIL_CAPTCHA_MAP_CACHE(self):
        return getattr(config, 'EMAIL_CAPTCHA_MAP_CACHE')

    @property
    def REDIS_THROTTLE_CACHE(self):
        return getattr(config, 'REDIS_THROTTLE_CACHE')

    @property
    def FROM_EAMIL(self):
        return getattr(config, 'FROM_EAMIL')

    @property
    def REGISTER_EMAIL_CAPTCHA_KEY_NAME(self):
        return getattr(config, 'REGISTER_EMAIL_CAPTCHA_KEY_NAME')

    @property
    def UPDATE_EMAIL_CAPTCHA_KEY_NAME(self):
        return getattr(config, 'UPDATE_EMAIL_CAPTCHA_KEY_NAME')

    @property
    def FORGOT_PASSWORD_CAPTCHA_KEY_NAME(self):
        return getattr(config, 'FORGOT_PASSWORD_CAPTCHA_KEY_NAME')

    @property
    def REDIS_CHECK_TASK_STATE(self):
        return getattr(config, 'REDIS_CHECK_TASK_STATE')

    @property
    def REDIS_TASK_QUEUE(self):
        return getattr(config, 'REDIS_TASK_QUEUE')

settings = Settings()