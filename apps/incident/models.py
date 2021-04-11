from django.db import models

from camera.models import Camera
from interface.models import AISkill
from rest_tools.get_user_model import User


class Incident(models.Model):
    """the incident that AI catched"""
    user = models.ForeignKey(verbose_name='所属用户', to=User, on_delete=models.CASCADE)
    incident_id = models.CharField(verbose_name='事件ID', max_length=50)
    camera = models.ForeignKey(verbose_name='所属设备', to=Camera, on_delete=models.CASCADE)
    ai_skill = models.ForeignKey(verbose_name='所用AI接口', to=AISkill, on_delete=models.CASCADE)

    # TODO change storage backend
    incident_image = models.ImageField(verbose_name='捕捉到的图片', upload_to='incident/%Y/%m/%d')
    response = models.TextField(verbose_name='请求响应')
    occurrence_time = models.DateTimeField(verbose_name='事件发生时间')

    class Meta:
        verbose_name = '事件总览'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'incident_id']
        ordering = ['-occurrence_time']

    def __str__(self):
        return self.camera.name