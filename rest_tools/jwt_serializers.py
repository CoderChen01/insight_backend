import re

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .get_user_model import User


def _login_by_email_authenticate(email, password):
    login_by_email_user = User.objects.filter(email=email).first()

    if login_by_email_user:
        if login_by_email_user.check_password(password):
            return login_by_email_user
        return
    return


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


class ExtendedTokenObtainSerializer(TokenObtainSerializer):
    """
    add email validator
    """

    email_field = User.EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField(
            required=False,
            validators=[
                username_validator,
            ],
        )
        self.fields[self.email_field] = serializers.EmailField(
            allow_blank=True,
            label="电子邮件地址",
            max_length=254,
            required=False,
            validators=[
                email_validator,
            ],
        )
        self.fields["password"] = serializers.CharField(
            min_length=6,
            max_length=16,
            validators=[
                password_validator,
            ],
        )
        self.user = None

    @classmethod
    def get_token(cls, user):
        raise NotImplementedError(
            "Must implement `get_token` method for `TokenObtainSerializer` subclasses"
        )

    def validate(self, attrs):
        username = attrs.get(self.username_field, False)
        email = attrs.get(self.email_field, False)

        if username and not email:
            authenticate_kwargs = {
                self.username_field: username,
                "password": attrs["password"],
            }

            try:
                authenticate_kwargs["request"] = self.context["request"]
            except KeyError:
                pass

            self.user = authenticate(**authenticate_kwargs)

        elif email and not username:
            self.user = _login_by_email_authenticate(email, attrs["password"])

        elif email and username:
            raise serializers.ValidationError(
                "邮箱或用户名不能同时传入"
            )  # represent validation failed
        else:
            raise serializers.ValidationError("账号必须传入")

        if self.user is None or not self.user.is_active:
            raise serializers.ValidationError(
                "账号或者密码错误"
            )  # represent validation failed

        return {}


class ExtendedTokenObtainPairSerializer(ExtendedTokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["username"] = self.user.username
        data["email"] = self.user.email
        data["nickname"] = self.user.nickname
        data["token"] = str(refresh.access_token)

        return data
