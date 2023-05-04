"""
celery tasks in user module
"""
from celery import shared_task
from django.core.mail import send_mail

from rest_tools.conf import settings
from rest_tools.email_templates.captcha_template import get_captcha_html
from rest_tools.gen_captcha import get_captcha
from rest_tools.redis_operations import SaveEmailCaptchaMap


@shared_task(ignore_result=True)
def send_email_captcha(email, context):
    """
    send email captcha and save map in redis
    :param email: email
    :param context: the class for captcha, a dict with only two key are 'flag' and 'text', flag is 'register' or 'update'.
    :return:
    """
    captcha = get_captcha()
    html_message = get_captcha_html(text=context["text"], captcha=captcha)

    subject = "insight - 验证码"
    from_email = settings.FROM_EAMIL

    with SaveEmailCaptchaMap(email=email, captcha=captcha) as save_obj:
        send_mail(
            subject=subject,
            from_email=from_email,
            message="insight - 验证码",
            recipient_list=[
                email,
            ],
            fail_silently=False,
            html_message=html_message,
        )

        if context["flag"] == "register":
            save_obj.save(settings.REGISTER_EMAIL_CAPTCHA_KEY_NAME)
        elif context["flag"] == "update":
            save_obj.save(settings.UPDATE_EMAIL_CAPTCHA_KEY_NAME)
        else:
            save_obj.save(settings.FORGOT_PASSWORD_CAPTCHA_KEY_NAME)
