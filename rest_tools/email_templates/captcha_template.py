from . import EMAIL_CAPTCHA_TEMPLATE


def get_captcha_html(text, captcha):
    html = EMAIL_CAPTCHA_TEMPLATE.replace('##text##', text).replace('##captcha##', captcha)

    return html