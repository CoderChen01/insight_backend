from camera.models import Camera
from django_celery_beat.models import PeriodicTask
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenViewBase
from user.tasks import send_email_captcha

from rest_tools.base_responses import BaseResponse
from rest_tools.conf import settings
from rest_tools.get_user_model import User
from rest_tools.jwt_serializers import ExtendedTokenObtainPairSerializer
from rest_tools.redis_operations import ValidateCaptcha
from rest_tools.redis_throttle import SendMailThrottle

from .serializers import (
    CloseUserSerializer,
    ForgotPasswordSerializer,
    HasUserSerializer,
    RegisterUserSerializer,
    SendEmailCaptchaSerializer,
    UpdateEmailSerializer,
    UpdatePasswordSerializer,
)


class SendEmailCaptcha(APIView):
    """
    Send email captcha
    """

    throttle_classes = (SendMailThrottle,)

    def get(self, request, *args, **kwargs):
        email_serializer = SendEmailCaptchaSerializer(
            data=request.query_params
        )

        if not email_serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if email_serializer.errors.get("email"):
                if email_serializer.errors["email"][0].code == "required":
                    retdata.error_msg = "邮箱是必传的"
                else:
                    retdata.error_msg = "邮箱格式错误或不支持的邮箱"
            elif email_serializer.errors.get("flag"):
                if email_serializer.errors["flag"][0].code == "required":
                    retdata.error_msg = "验证码类型是必传的"
            return Response(retdata.result)

        email = email_serializer.validated_data["email"]
        flag = email_serializer.validated_data["flag"]

        if flag == "register":
            context = {"text": "注册", "flag": flag}
        elif flag == "update":
            context = {"text": "修改邮件", "flag": flag}
        else:
            context = {"text": "找回密码", "flag": flag}

        send_email_captcha.delay(email, context)

        retdata = BaseResponse(code=1, msg="success", success_msg="验证码发送成功")
        return Response(retdata.result)


class RegisterView(APIView):
    """
    Handle registering
    """

    def post(self, request, *args, **kwargs):
        user_serializer = RegisterUserSerializer(data=request.data)

        if not user_serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if user_serializer.errors.get("captcha"):
                if user_serializer.errors["captcha"][0].code == "required":
                    retdata.error_msg = "验证码是必传的"
                else:
                    retdata.error_msg = "验证码格式错误，为5位数字"
            elif user_serializer.errors.get("username"):
                if user_serializer.errors["username"][0].code == "required":
                    retdata.error_msg = "用户名是必传的"
                else:
                    retdata.error_msg = "用户名不合法，为6到16位字母、数字或下划线"
            elif user_serializer.errors.get("nickname"):
                if user_serializer.errors["nickname"][0].code == "required":
                    retdata.error_msg = "昵称是必传的"
                else:
                    retdata.error_msg = "昵称不合法, 不得超过20个字符"
            elif user_serializer.errors.get("password"):
                if user_serializer.errors["password"][0].code == "required":
                    retdata.error_msg = "密码是必传的"
                else:
                    retdata.error_msg = "密码不合法，为6到16位字母、数字或合法符号"
            elif user_serializer.errors.get("email"):
                if user_serializer.errors["email"][0].code == "required":
                    retdata.error_msg = "邮箱是必传的"
                else:
                    retdata.error_msg = "邮箱格式错误或不支持的邮箱"
            return Response(retdata.result)

        username = user_serializer.validated_data.get("username")
        email = user_serializer.validated_data.get("email")
        captcha = user_serializer.validated_data.get("captcha")

        has_username = User.objects.filter(username=username).first()
        has_email = User.objects.filter(email=email).first()

        if not has_username and not has_email:
            with ValidateCaptcha(
                email=email, captcha=captcha
            ) as captcha_validator:
                ret = captcha_validator.validate(
                    settings.REGISTER_EMAIL_CAPTCHA_KEY_NAME
                )

                if not ret["flag"]:
                    retdata = BaseResponse(
                        code=0, msg="error", error_msg=ret["result"]
                    )
                    return Response(retdata.result)

            user_serializer.save()
            retdata = BaseResponse(code=1, msg="success", success_msg="用户创建成功")
            return Response(retdata.result)

        retdata = BaseResponse(code=0, msg="error", error_msg="用户名或邮箱已存在")
        return Response(retdata.result)

    def get(self, request, *args, **kwargs):
        """
        Check if user exists
        """
        if not request.query_params:
            retdata = BaseResponse(code=0, msg="error", error_msg="传入参数不能为空")
            return Response(retdata.result)

        query_serializer = HasUserSerializer(data=request.query_params)

        if not query_serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if query_serializer.errors.get("email"):
                retdata.error_msg = "邮箱格式错误或不支持的邮箱"
            elif query_serializer.errors.get("username"):
                retdata.error_msg = "用户名不合法，为6到16位字母、数字或下划线"
            return Response(retdata.result)

        username = query_serializer.validated_data.get("username", False)
        email = query_serializer.validated_data.get("email", False)

        if username and not email:
            has_user_username = User.objects.filter(username=username).first()

            if has_user_username:
                retdata = BaseResponse(
                    code=1, msg="success", data=1, success_msg="用户名已存在"
                )
                return Response(retdata.result)

            retdata = BaseResponse(
                code=1, msg="success", data=0, success_msg="用户名不存在，可创建"
            )
            return Response(retdata.result)

        elif email and not username:
            has_user_email = User.objects.filter(email=email).first()

            if has_user_email:
                retdata = BaseResponse(
                    code=1, msg="success", data=1, success_msg="该邮箱已绑定其他用户"
                )
                return Response(retdata.result)
            retdata = BaseResponse(
                code=1, msg="success", data=0, success_msg="该邮箱未绑定其他用户，可绑定新用户"
            )
            return Response(retdata.result)

        else:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="用户名和邮箱不能同时传入或请求参数不合法"
            )
            return Response(retdata.result)


class LoginView(TokenViewBase):
    """
    Override token view
    """

    serializer_class = ExtendedTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            retdata = BaseResponse(
                code=1,
                msg="success",
                data=serializer.validated_data,
                success_msg="登录成功",
            )
            return Response(retdata.result)

        retdata = BaseResponse(code=0, msg="error")
        non_field_errors = serializer.errors.get("non_field_errors")
        if non_field_errors:
            retdata.error_msg = non_field_errors[0]
            return Response(retdata.result)
        elif serializer.errors.get("username"):
            retdata.error_msg = "用户名不合法，为6到16位字母、数字或下划线"
        elif serializer.errors.get("email"):
            retdata.error_msg = "邮箱格式错误或不支持的邮箱"
        elif serializer.errors.get("password"):
            if serializer.errors["password"][0].code == "required":
                retdata.error_msg = "账号或密码是必传的"
            else:
                retdata.error_msg = "密码不合法，为6到16位字母、数字或合法符号"
        return Response(retdata.result)


class ForgotPasswordView(APIView):
    """
    if you forgot your password, you can change password by thsi view.
    """

    def patch(self, request, *args, **kwargs):
        data_serializer = ForgotPasswordSerializer(data=request.data)

        if not data_serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if data_serializer.errors.get("email"):
                if data_serializer.errors["email"][0].code == "required":
                    retdata.error_msg = "邮箱是必传的"
                else:
                    retdata.error_msg = "邮箱格式不合法或不支持的邮箱"
            elif data_serializer.errors.get("new_password"):
                if (
                    data_serializer.errors["new_password"][0].code
                    == "required"
                ):
                    retdata.error_msg = "新密码是必传的"
                else:
                    retdata.error_msg = "密码不合法，为6到16位字母、数字或合法符号"
            elif data_serializer.errors.get("captcha"):
                if data_serializer.errors["captcha"][0].code == "required":
                    retdata.error_msg = "验证码是必传的"
                else:
                    retdata.error_msg = "验证码格式错误，为5位数字"
            return Response(retdata.result)

        email = data_serializer.validated_data["email"]
        captcha = data_serializer.validated_data["captcha"]
        new_password = data_serializer.validated_data["new_password"]

        user_obj = User.objects.filter(email=email).first()

        if user_obj:
            with ValidateCaptcha(
                email=email, captcha=captcha
            ) as captcha_validator:
                ret = captcha_validator.validate(
                    settings.FORGOT_PASSWORD_CAPTCHA_KEY_NAME
                )

                if not ret["flag"]:
                    retdata = BaseResponse(
                        code=0, msg="error", error_msg=ret["result"]
                    )
                    return Response(retdata.result)

            user_obj.set_password(new_password)
            user_obj.save()

            retdata = BaseResponse(code=1, msg="success", success_msg="找回密码成功")
            return Response(retdata.result)

        retdata = BaseResponse(code=0, msg="error", error_msg="账户不存在")
        return Response(retdata.result)


class UpdatePasswordView(APIView):
    """
    update your password
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        user_serializer = UpdatePasswordSerializer(data=request.data)

        if not user_serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if user_serializer.errors.get("username"):
                retdata.error_msg = "用户名不合法，为6到16位字母、数字或下划线"
            elif user_serializer.errors.get("email"):
                retdata.error_msg = "邮箱格式错误或不支持的邮箱"
            elif user_serializer.errors.get("password"):
                if user_serializer.errors["password"][0].code == "required":
                    retdata.error_msg = "账号或密码是必须的"
                else:
                    retdata.error_msg = "密码不合法，为6到16位字母、数字或合法符号"
            elif user_serializer.errors.get("new_password"):
                if (
                    user_serializer.errors["new_password"][0].code
                    == "required"
                ):
                    retdata.error_msg = "新密码是必须的"
                else:
                    retdata.error_msg = "密码不合法，为6到16位字母、数字或合法符号"
            return Response(retdata.result)

        username = user_serializer.validated_data.get("username", False)
        email = user_serializer.validated_data.get("email", False)
        password = user_serializer.validated_data["password"]
        new_password = user_serializer.validated_data["new_password"]

        if username and not email:
            user_obj = User.objects.filter(username=username).first()
        elif email and not username:
            user_obj = User.objects.filter(email=email).first()
        elif email and username:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="邮箱和用户名不能同时传入"
            )
            return Response(retdata.result)
        else:
            retdata = BaseResponse(code=0, msg="error", error_msg="账号是必须的")
            return Response(retdata.result)

        if user_obj is None:
            retdata = BaseResponse(code=0, msg="error", error_msg="用户不存在")
            return Response(retdata.result)

        elif user_obj.check_password(raw_password=password):
            user_obj.set_password(new_password)
            user_obj.save()

            retdata = BaseResponse(code=1, msg="success", success_msg="密码修改成功")
            return Response(retdata.result)

        retdata = BaseResponse(code=0, msg="error", error_msg="原密码错误")
        return Response(retdata.result)


class UpdateEmailView(APIView):
    """
    update email
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        data_serializer = UpdateEmailSerializer(data=request.data)

        if not data_serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if data_serializer.errors.get("username"):
                retdata.error_msg = "用户名不合法，为6到16位字母、数字或下划线"
            elif data_serializer.errors.get("email"):
                retdata.error_msg = "邮箱格式错误或不支持的邮箱"
            elif data_serializer.errors.get("password"):
                if data_serializer.errors["password"][0].code == "required":
                    retdata.error_msg = "账号或密码是必须的"
                else:
                    retdata.error_msg = "密码不合法，为6到16位字母、数字或合法符号"
            elif data_serializer.errors.get("new_email"):
                if data_serializer.errors["new_email"][0].code == "required":
                    retdata.error_msg = "新邮箱是必须的"
                else:
                    retdata.error_msg = "新邮箱格式错误或不支持的邮箱"
            elif data_serializer.errors.get("captcha"):
                if data_serializer.errors["captcha"][0].code == "required":
                    retdata.error_msg = "验证码是必须的"
                else:
                    retdata.error_msg = "验证码格式错误，为5位数字"
            return Response(retdata.result)

        username = data_serializer.validated_data.get("username", False)
        email = data_serializer.validated_data.get("email", False)
        captcha = data_serializer.validated_data["captcha"]
        new_email = data_serializer.validated_data["new_email"]
        password = data_serializer.validated_data["password"]

        if username and not email:
            user_obj = User.objects.filter(username=username).first()
        elif email and not username:
            user_obj = User.objects.filter(email=email).first()
        elif email and username:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="用户名与邮箱不能同时传入"
            )
            return Response(retdata.result)
        else:
            retdata = BaseResponse(code=0, msg="error", error_msg="账号必须传入")
            return Response(retdata.result)

        has_email = User.objects.filter(email=new_email).first()

        flag = user_obj and not has_email
        if flag:
            with ValidateCaptcha(
                email=new_email, captcha=captcha
            ) as captcha_validator:
                ret = captcha_validator.validate(
                    settings.UPDATE_EMAIL_CAPTCHA_KEY_NAME
                )

                if not ret["flag"]:
                    retdata = BaseResponse(
                        code=0, msg="error", error_msg=ret["result"]
                    )
                    return Response(retdata.result)

            if user_obj.check_password(raw_password=password):
                user_obj.email = new_email
                user_obj.save()

                retdata = BaseResponse(
                    code=1, msg="success", success_msg="修改邮件成功"
                )
                return Response(retdata.result)

            retdata = BaseResponse(
                code=0, msg="error", error_msg="用户验证失败，密码错误"
            )
            return Response(retdata.result)

        elif not user_obj:
            retdata = BaseResponse(code=0, msg="error", error_msg="账户不存在")
            return Response(retdata.result)

        retdata = BaseResponse(code=0, msg="error", error_msg="新邮件已绑定到其他用户")
        return Response(retdata.result)


class CloseUser(APIView):
    """logout an user"""

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        user_serializer = CloseUserSerializer(data=request.data)

        if not user_serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if user_serializer.errors.get("username"):
                retdata.error_msg = "用户名不合法，为6到16位字母、数字或下划线"
            elif user_serializer.errors.get("email"):
                retdata.error_msg = "邮箱格式错误或不支持的邮箱"
            elif user_serializer.errors.get("password"):
                if user_serializer.errors["password"][0].code == "required":
                    retdata.error_msg = "账号或密码是必须的"
                else:
                    retdata.error_msg = "密码不合法，为6到16位字母、数字或合法符号"
            elif user_serializer.errors.get("force"):
                retdata.error_msg = "force字段是bool类型"
            return Response(retdata.result)

        username = user_serializer.validated_data.get("username", False)
        email = user_serializer.validated_data.get("email", False)
        password = user_serializer.validated_data["password"]

        if username and not email:
            user_obj = User.objects.filter(username=username).first()
        elif email and not username:
            user_obj = User.objects.filter(email=email).first()
        elif email and username:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="用户名和邮箱不能同时传入"
            )
            return Response(retdata.result)
        else:
            retdata = BaseResponse(code=0, msg="error", error_msg="账号是必须的")
            return Response(retdata.result)

        if not user_obj:
            retdata = BaseResponse(code=0, msg="error", error_msg="该用户未注册")
            return Response(retdata.result)

        if not user_obj.check_password(raw_password=password):
            retdata = BaseResponse(code=0, msg="error", error_msg="密码错误")
            return Response(retdata.result)

        cameras = Camera.objects.filter(user=user_obj)
        if cameras:
            for camera in cameras:
                if camera.state in (20, 21, 22):
                    if not user_serializer.validated_data["force"]:
                        retdata = BaseResponse(
                            code=0, msg="error", error_msg="该用户存在执行任务"
                        )
                        return Response(retdata.result)

                    task_id = user_obj.username + "_" + camera.camera_id
                    periodic_task = PeriodicTask.objects.filter(
                        name=task_id
                    ).first()
                    periodic_task.enabled = False
                    periodic_task.save()
                    periodic_task.delete()

        user_obj.delete()
        retdata = BaseResponse(code=1, msg="success", success_msg="用户注销成功")
        return Response(retdata.result)


class IsExpired(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        retdata = BaseResponse(code=1, msg="success", success_msg="Token未过期")
        return Response(retdata.result)
