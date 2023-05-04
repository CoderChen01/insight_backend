from rest_framework.exceptions import (
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    ParseError,
    Throttled,
    UnsupportedMediaType,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

from .base_responses import BaseResponse


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, ParseError):
            retdata = BaseResponse(code=0, msg="error", error_msg="JSON数据不合法")
            return Response(retdata.result)

        if isinstance(exc, MethodNotAllowed):
            retdata = BaseResponse(code=0, msg="error", error_msg="当前请求方法不被允许")
            return Response(retdata.result)

        if isinstance(exc, Throttled):
            retdata = BaseResponse(
                code=0,
                msg="error",
                error_msg="请求过于频繁, 请于{seconds}秒后重试".format(seconds=exc.wait),
            )
            return Response(retdata.result)

        if isinstance(exc, AuthenticationFailed) or isinstance(
            exc, NotAuthenticated
        ):
            retdata = BaseResponse(
                code=0, msg="error", error_msg="认证失败，请提供正确的认证Token"
            )
            return Response(retdata.result)

        if isinstance(exc, UnsupportedMediaType):
            retdata = BaseResponse(
                code=0, msg="error", error_msg="不支持的MediaType"
            )
            return Response(retdata.result)

    return response
