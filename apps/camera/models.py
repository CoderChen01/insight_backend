from django.db import models
from face.models import FaceGroup
from interface.models import AISkill

from rest_tools.get_user_model import User

__all__ = [
    "FaceSettings",
    "CameraExtractionSettings",
    "AISkillSettings",
    "CameraGroup",
    "Camera",
]


class FaceSettings(models.Model):
    QUALITY_CHOICES = ((0, "无"), (1, "低"), (2, "中"), (3, "高"))

    face_group = models.ManyToManyField(verbose_name="关联人脸组", to=FaceGroup)
    similarity = models.FloatField(verbose_name="相似度阈值")
    quality = models.IntegerField(verbose_name="质量要求", choices=QUALITY_CHOICES)

    class Meta:
        verbose_name = "人脸库设置"
        verbose_name_plural = verbose_name


class CameraExtractionSettings(models.Model):
    FREQUENCY_CHOICES = ((1, "每1秒抽取1张图片"), (2, "每2秒抽取1张图片"), (3, "每2秒抽取1张图片"))
    frequency = models.IntegerField(
        verbose_name="抽帧频率", choices=FREQUENCY_CHOICES
    )
    start_time = models.TimeField(verbose_name="开始时间")
    end_time = models.TimeField(verbose_name="结束时间")

    class Meta:
        verbose_name = "摄像头抽帧设置"
        verbose_name_plural = verbose_name


class AISkillSettings(models.Model):
    """AI skill settings"""

    ai_skill = models.ForeignKey(
        verbose_name="AI技能绑定", to=AISkill, on_delete=models.CASCADE
    )
    coordinates = models.CharField(verbose_name="图像划分区域坐标", max_length=255)
    face_relevance = models.ForeignKey(
        verbose_name="人脸库关联(可选)",
        null=True,
        blank=True,
        to="FaceSettings",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "AI技能配置"
        verbose_name_plural = verbose_name


class CameraGroup(models.Model):
    """the cameras group"""

    user = models.ForeignKey(
        verbose_name="所属用户", to=User, on_delete=models.CASCADE
    )
    camera_group_id = models.CharField(verbose_name="摄像头组ID", max_length=50)
    name = models.CharField(verbose_name="分组名", max_length=30)
    description = models.CharField(
        verbose_name="分组描述", max_length=300, default="", blank=True
    )
    add_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    class Meta:
        verbose_name = "摄像头分组"
        verbose_name_plural = verbose_name
        unique_together = ["user", "camera_group_id"]

    def __str__(self):
        return self.name


class Camera(models.Model):
    """camera info"""

    STATE_CHOICES = (
        (10, "连接失败"),
        (11, "连接成功"),
        (12, "抽帧已配置"),
        (13, "配置完成"),
        (20, "工作中出错"),
        (21, "工作中"),
        (22, "已暂停"),
    )

    user = models.ForeignKey(
        verbose_name="所属用户", to=User, on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        verbose_name="所属分组", to="CameraGroup", on_delete=models.CASCADE
    )

    # AI skill settings
    ai_skill_settings = models.ManyToManyField(
        verbose_name="所用AI技能", blank=True, to="AISkillSettings"
    )  # null has no effect on ManyToManyFild

    # extraction settings
    extraction_settings = models.OneToOneField(
        verbose_name="抽帧设置",
        null=True,
        blank=True,
        to="CameraExtractionSettings",
        on_delete=models.CASCADE,
    )

    # base settings
    camera_id = models.CharField(verbose_name="摄像头ID", max_length=50)
    name = models.CharField(verbose_name="摄像头名称", max_length=30)
    description = models.CharField(
        verbose_name="摄像头描述", max_length=300, default="", blank=True
    )
    camera_url = models.CharField(verbose_name="视频流地址", max_length=255)
    state = models.IntegerField(verbose_name="摄像头状态", choices=STATE_CHOICES)
    add_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    class Meta:
        verbose_name = "摄像头配置"
        verbose_name_plural = verbose_name
        unique_together = ["user", "camera_id"]

    def __str__(self):
        return self.name
