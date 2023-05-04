from django.db import models

from rest_tools.get_user_model import User


class FaceGroup(models.Model):
    """the face  group"""

    user = models.ForeignKey(
        verbose_name="所属用户", to=User, on_delete=models.CASCADE
    )
    face_group_id = models.CharField(verbose_name="人脸组ID", max_length=50)
    name = models.CharField(verbose_name="分组名", max_length=30)
    description = models.CharField(
        verbose_name="分组描述", max_length=300, default=""
    )
    bound = models.BooleanField(verbose_name="是否被使用", default=False)
    add_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    class Meta:
        verbose_name = "人脸库分组"
        verbose_name_plural = verbose_name
        unique_together = ["user", "face_group_id"]

    def __str__(self):
        return self.name


class Face(models.Model):
    """the face"""

    user = models.ForeignKey(
        verbose_name="所属用户", to=User, on_delete=models.CASCADE
    )
    face_id = models.CharField(verbose_name="人脸ID", max_length=50)
    group = models.ForeignKey(
        verbose_name="所属分组", to="FaceGroup", on_delete=models.CASCADE
    )
    name = models.CharField(verbose_name="姓名", max_length=30)
    # TODO change storage backend
    face_image = models.ImageField(
        verbose_name="人脸照片", upload_to="faces/%Y/%m/%d"
    )
    add_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    class Meta:
        verbose_name = "人脸上传"
        verbose_name_plural = verbose_name
        unique_together = ["user", "face_id"]

    def __str__(self):
        return self.name
