import re

from rest_framework import serializers

from rest_tools.get_user_model import User
from rest_tools.id_validator import id_validator


def username_validator(value):
    has_cn = re.search("[\u4e00-\u9fa5]+", value)
    if has_cn:
        raise serializers.ValidationError("用户名不能有中文")


def email_validator(value):
    domains = [
        "qq.com",
        "163.com",
        "vip.163.com",
        "263.net",
        "yeah.net",
        "sohu.com",
        "sina.cn",
        "sina.com",
        "eyou.com",
        "gmail.com",
        "hotmail.com",
        "42du.cn",
    ]
    if "@" in value:
        if value.split("@")[1] not in domains:
            raise serializers.ValidationError("不支持的邮箱")


def password_validator(value):
    has_cn = re.search("[\u4e00-\u9fa5]+", value)
    if has_cn:
        raise serializers.ValidationError("密码不能有中文")


def captcha_validator(value):
    if len(value) != 5:
        raise serializers.ValidationError("长度应为5")

    for char in value:
        if char < "0" or char > "9":
            raise serializers.ValidationError("验证码为纯数字")


class SendEmailCaptchaSerializer(serializers.Serializer):
    """
    serialize the request data when user send email captcha.
    """

    email = serializers.EmailField(
        max_length=254,
        validators=[
            email_validator,
        ],
    )
    flag = serializers.CharField(max_length=8)

    def validate_flag(self, value):
        choices = ("register", "update", "forget")

        if value not in choices:
            raise serializers.ValidationError()

        return value


class HasUserSerializer(serializers.ModelSerializer):
    """
    the serializer used to views that check if user exits
    """

    username = serializers.CharField(
        label="用户名",
        max_length=150,
        validators=[id_validator, username_validator],
        required=False,
    )

    class Meta:
        model = User
        fields = ("username", "email")
        extra_kwargs = {
            "email": {
                "required": False,
                "validators": [
                    email_validator,
                ],
            }
        }


class RegisterUserSerializer(serializers.ModelSerializer):
    """
    The user serializer
    """

    username = serializers.CharField(
        label="用户名",
        min_length=6,
        max_length=16,
        validators=[id_validator, username_validator],
    )
    captcha = serializers.CharField(
        write_only=True,
        validators=[
            captcha_validator,
        ],
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "nickname", "captcha")
        extra_kwargs = {
            "password": {
                "min_length": 6,
                "max_length": 16,
                "write_only": True,
                "validators": [
                    password_validator,
                ],
            },
            "nickname": {"max_length": 20, "required": True},
        }

    def create(self, validated_data):
        """
        create an user
        :param validated_data: validated data
        :return: user obj
        """
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            nickname=validated_data["nickname"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UpdatePasswordSerializer(serializers.ModelSerializer):
    """
    serialize the request data when user change password.
    """

    username = serializers.CharField(
        label="用户名",
        min_length=6,
        max_length=16,
        required=False,
        validators=[id_validator, username_validator],
    )
    new_password = serializers.CharField(
        min_length=6,
        max_length=16,
        validators=[
            password_validator,
        ],
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "new_password")
        extra_kwargs = {
            "email": {
                "required": False,
                "validators": [
                    email_validator,
                ],
            },
            "password": {
                "min_length": 6,
                "max_length": 16,
                "validators": [
                    password_validator,
                ],
            },
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254,
        validators=[
            email_validator,
        ],
    )
    captcha = serializers.CharField(
        validators=[
            captcha_validator,
        ]
    )
    new_password = serializers.CharField(
        min_length=6,
        max_length=16,
        validators=[
            password_validator,
        ],
    )


class UpdateEmailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        label="用户名",
        min_length=6,
        max_length=16,
        required=False,
        validators=[id_validator, username_validator],
    )
    new_email = serializers.EmailField(
        max_length=254,
        validators=[
            email_validator,
        ],
    )
    captcha = serializers.CharField(
        validators=[
            captcha_validator,
        ]
    )

    class Meta:
        model = User
        fields = ("username", "email", "password", "new_email", "captcha")
        extra_kwargs = {
            "email": {
                "required": False,
                "validators": [
                    email_validator,
                ],
            },
            "password": {
                "min_length": 6,
                "max_length": 16,
                "validators": [
                    password_validator,
                ],
            },
        }


class CloseUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        label="用户名",
        min_length=6,
        max_length=16,
        required=False,
        validators=[id_validator, username_validator],
    )
    force = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ("username", "email", "password", "force")
        extra_kwargs = {
            "email": {
                "required": False,
                "validators": [
                    email_validator,
                ],
            },
            "password": {
                "min_length": 6,
                "max_length": 16,
                "validators": [
                    password_validator,
                ],
            },
        }
