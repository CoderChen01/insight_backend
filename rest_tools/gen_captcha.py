import random


BASE_STRING = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def get_captcha():
    captcha = ''.join(random.choices(BASE_STRING, k=5))

    return captcha
