from django.db import models

from rest_tools.get_user_model import User


class AISkillGroup(models.Model):
    """the AI interface group"""

    user = models.ForeignKey(
        verbose_name="所属用户", to=User, on_delete=models.CASCADE
    )
    ai_skill_group_id = models.CharField(verbose_name="AI技能组ID", max_length=50)
    name = models.CharField(verbose_name="分组名", max_length=30)
    description = models.CharField(
        verbose_name="分组描述", max_length=300, default="", blank=True, null=True
    )
    add_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)

    class Meta:
        verbose_name = "AI技能接口分组"
        verbose_name_plural = verbose_name
        unique_together = ["user", "ai_skill_group_id"]

    def __str__(self):
        return self.name


class AISkill(models.Model):
    """the AI interface info"""

    STATE_CHOICES = ((0, "接口异常"), (1, "接口正常"))

    user = models.ForeignKey(
        verbose_name="所属用户", to=User, on_delete=models.CASCADE
    )
    ai_skill_id = models.CharField(verbose_name="AI技能ID", max_length=50)
    group = models.ForeignKey(
        verbose_name="所属分组", to="AISkillGroup", on_delete=models.CASCADE
    )
    name = models.CharField(verbose_name="接口名称", max_length=30)
    description = models.CharField(
        verbose_name="接口描述", max_length=300, default="", blank=True, null=True
    )
    add_time = models.DateTimeField(verbose_name="最后修改时间", auto_now=True)
    ai_skill_url = models.CharField(verbose_name="技能接口URL", max_length=512)
    state = models.IntegerField(verbose_name="接口状态", choices=STATE_CHOICES)
    bound = models.BooleanField(verbose_name="是否被使用", default=False)

    class Meta:
        verbose_name = "AI技能接口配置"
        verbose_name_plural = verbose_name
        unique_together = ["user", "ai_skill_id"]

    def __str__(self):
        return self.name
