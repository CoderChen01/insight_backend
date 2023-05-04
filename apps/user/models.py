from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    """
    Define the user infomantion
    """

    nickname = models.CharField(verbose_name="用户昵称", max_length=16, default="")

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
