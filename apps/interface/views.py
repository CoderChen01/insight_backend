import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_tools.base_responses import BaseResponse

from .models import AISkill, AISkillGroup
from .serializers import (
    InterfaceGroupIDSerializer,
    InterfaceGroupSerializer,
    InterfaceIDSerializer,
    InterfaceSerializer,
    UpdateInterfaceSerializer,
)

__all__ = [
    "CreateInterfaceGroup",
    "RetrieveInterfaceGroup",
    "UpdateInterfaceGroup",
    "DeleteInterfaceGroup",
    "CreateInterface",
    "RetrieveInterface",
    "UpdateInterface",
    "DeleteInterface",
    "RefreshState",
]


class CreateInterfaceGroup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = InterfaceGroupSerializer(data=request.data)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_group_id"):
                if (
                    serializer.errors["ai_skill_group_id"][0].code
                    == "required"
                ):
                    retdata.error_msg = "技能分组ID是必须的"
                else:
                    retdata.error_msg = "技能分组ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("name"):
                if serializer.errors["name"][0].code == "required":
                    retdata.error_msg = "技能名称是必须的"
                else:
                    retdata.error_msg = "技能分组名称不能超过30个字符或为空"
            elif serializer.errors.get("description"):
                retdata.error_msg = "技能分组描述不能超过300个字符"
            return Response(retdata.result)

        has_ai_skill_group = AISkillGroup.objects.filter(
            user=request.user,
            ai_skill_group_id=serializer.validated_data["ai_skill_group_id"],
        ).first()
        if has_ai_skill_group:
            retdata = BaseResponse(code=0, msg="error", error_msg="已存在接口库")
            return Response(retdata.result)

        ai_skill_group_obj = serializer.save(user=request.user)
        retdata = BaseResponse(
            code=1,
            msg="success",
            data=InterfaceGroupSerializer(ai_skill_group_obj).data,
            success_msg="接口库创建成功",
        )
        return Response(retdata.result)

    def get(self, request, *args, **kwargs):
        serializer = InterfaceGroupIDSerializer(data=request.query_params)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_group_id"):
                if (
                    serializer.errors["ai_skill_group_id"][0].code
                    == "required"
                ):
                    retdata.error_msg = "技能接口分组ID是必须的"
                else:
                    retdata.error_msg = "技能接口分组ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        has_ai_skill_gourp = AISkillGroup.objects.filter(
            user=request.user,
            ai_skill_group_id=serializer.validated_data["ai_skill_group_id"],
        ).first()
        retdata = BaseResponse(code=1, msg="success")
        if not has_ai_skill_gourp:
            retdata.success_msg = "技能接口分组不存在，可创建"
            retdata.data = 0
        else:
            retdata.success_msg = "技能接口分组已存在"
            retdata.data = 1

        return Response(retdata.result)


class RetrieveInterfaceGroup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        ai_skill_groups = AISkillGroup.objects.filter(user=request.user)
        serializer = InterfaceGroupSerializer(ai_skill_groups, many=True)

        retdata = BaseResponse(
            code=1,
            msg="success",
            success_msg="接口库数据请求成功",
            data=serializer.data,
        )
        return Response(retdata.result)


class UpdateInterfaceGroup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        ai_skill_groups = AISkillGroup.objects.filter(user=request.user)
        serializer = InterfaceGroupSerializer(
            instance=ai_skill_groups, data=request.data, partial=True
        )

        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_group_id"):
                retdata.error_msg = "接口分组ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("name"):
                retdata.error_msg = "技能分组名称不能超过30个字符或为空"
            elif serializer.errors.get("description"):
                retdata.error_msg = "技能分组描述不能超过300个字符"
            return Response(retdata.result)

        ai_skill_group_id = serializer.validated_data.get("ai_skill_group_id")
        name = serializer.validated_data.get("name")
        description = serializer.validated_data.get("description")
        if not ai_skill_group_id:
            retdata = BaseResponse(code=0, msg="error", error_msg="接口库ID是必须的")
            return Response(retdata.result)

        if not name and not description:
            retdata = BaseResponse(code=0, msg="error", error_msg="请传入须修改的参数")
            return Response(retdata.result)

        ai_skill_group = ai_skill_groups.filter(
            ai_skill_group_id=ai_skill_group_id
        ).first()
        if not ai_skill_group:
            retdata = BaseResponse(code=0, msg="error", error_msg="接口库不存在")
            return Response(retdata.result)

        ai_skills = ai_skill_group.aiskill_set.all()
        if ai_skills:
            for ai_skill in ai_skills:
                if ai_skill.bound:
                    retdata = BaseResponse(
                        code=0,
                        msg="error",
                        error_msg="该技能接口库中存在绑定摄像头的接口，无法修改信息",
                    )
                    return Response(retdata.result)

        new_ai_skill_group_obj = serializer.save()
        retdata = BaseResponse(
            code=1,
            msg="success",
            success_msg="接口库信息更改成功",
            data=InterfaceGroupSerializer(new_ai_skill_group_obj).data,
        )
        return Response(retdata.result)


class DeleteInterfaceGroup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        serializer = InterfaceGroupIDSerializer(data=request.data)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_group_id"):
                if (
                    serializer.errors["ai_skill_group_id"][0].code
                    == "required"
                ):
                    retdata.error_msg = "技能分组ID是必须的"
                else:
                    retdata.error_msg = "技能分组ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        ai_skill_group = AISkillGroup.objects.filter(
            user=request.user,
            ai_skill_group_id=serializer.validated_data["ai_skill_group_id"],
        ).first()
        if not ai_skill_group:
            retdata = BaseResponse(code=0, msg="error", error_msg="不存在的接口库")
            return Response(retdata.result)

        ai_skills = ai_skill_group.aiskill_set.all()
        if ai_skills:
            for ai_skill in ai_skills:
                if ai_skill.bound:
                    retdata = BaseResponse(
                        code=0, msg="error", error_msg="该技能接口库中存在绑定摄像头的接口，无法删除"
                    )
                    return Response(retdata.result)

        ai_skill_group.delete()
        retdata = BaseResponse(code=1, msg="success", success_msg="接口库删除成功")
        return Response(retdata.result)


class CreateInterface(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = InterfaceSerializer(data=request.data)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_id"):
                if serializer.errors["ai_skill_id"][0].code == "required":
                    retdata.error_msg = "技能接口ID是必须的"
                else:
                    retdata.error_msg = "技能接口ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("ai_skill_group_id"):
                if (
                    serializer.errors["ai_skill_group_id"][0].code
                    == "required"
                ):
                    retdata.error_msg = "技能分组接口ID是必须的"
                else:
                    retdata.error_msg = "技能分组接口ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("name"):
                if serializer.errors["name"][0].code == "required":
                    retdata.error_msg = "技能接口名称是必须的"
                else:
                    retdata.error_msg = "技能接口名称不能超过30个字符或为空"
            elif serializer.errors.get("ai_skill_url"):
                if serializer.errors["ai_skill_url"][0].code == "required":
                    retdata.error_msg = "技能接口地址是必须的"
                else:
                    retdata.error_msg = serializer.errors["ai_skill_url"][0]
            elif serializer.errors.get("description"):
                retdata.error_msg = "技能接口描述不能超过300个字符"
            return Response(retdata.result)

        has_ai_skill = AISkill.objects.filter(
            user=request.user,
            ai_skill_id=serializer.validated_data["ai_skill_id"],
        ).first()
        if has_ai_skill:
            retdata = BaseResponse(code=0, msg="error", error_msg="AI技能接口已存在")
            return Response(retdata.result)

        has_ai_skill_group = AISkillGroup.objects.filter(
            user=request.user,
            ai_skill_group_id=serializer.validated_data["ai_skill_group_id"],
        ).first()
        if not has_ai_skill_group:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="不存在的技能接口库，无法绑定技能接口"
            )
            return Response(retdata.result)

        ai_skill_obj = serializer.save(user=request.user)
        retdata = BaseResponse(
            code=1,
            msg="success",
            success_msg="AI技能接口创建完成",
            data=InterfaceSerializer(ai_skill_obj).data,
        )
        return Response(retdata.result)

    def get(self, request, *args, **kwargs):
        serializer = InterfaceIDSerializer(data=request.query_params)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_id"):
                if serializer.errors["ai_skill_id"][0].code == "required":
                    retdata.error_msg = "技能接口ID是必须的"
                else:
                    retdata.error_msg = "技能接口ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        has_ai_skill = AISkill.objects.filter(
            user=request.user,
            ai_skill_id=serializer.validated_data["ai_skill_id"],
        ).first()
        retdata = BaseResponse(code=1, msg="success")
        if not has_ai_skill:
            retdata.success_msg = "技能接口不存在，可创建"
            retdata.data = 0
        else:
            retdata.success_msg = "技能接口已存在"
            retdata.data = 1

        return Response(retdata.result)


class RetrieveInterface(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = InterfaceGroupIDSerializer(data=request.query_params)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_group_id"):
                if (
                    serializer.errors["ai_skill_group_id"][0].code
                    == "required"
                ):
                    retdata.error_msg = "技能接口分组是必须的"
                else:
                    retdata.error_msg = "技能接口分组ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        ai_skill_group = AISkillGroup.objects.filter(
            user=request.user,
            ai_skill_group_id=serializer.validated_data["ai_skill_group_id"],
        ).first()
        if not ai_skill_group:
            retdata = BaseResponse(code=0, msg="error", error_msg="不存在的接口库")
            return Response(retdata.result)

        ai_skills = ai_skill_group.aiskill_set.all()
        ai_skills_serializer = InterfaceSerializer(ai_skills, many=True)
        retdata = BaseResponse(
            code=1,
            msg="success",
            success_msg="AI技能接口请求成功",
            data=ai_skills_serializer.data,
        )
        return Response(retdata.result)


class UpdateInterface(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        ai_skills = AISkill.objects.filter(user=request.user)
        serializer = UpdateInterfaceSerializer(
            instance=ai_skills, data=request.data, partial=True
        )

        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_id"):
                retdata.error_msg = "技能接口ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("name"):
                retdata.error_msg = "技能接口名称不能超过30个字符或为空"
            elif serializer.errors.get("description"):
                retdata.error_msg = "技能接口描述不能超过300个字符"
            elif serializer.errors.get("ai_skill_url"):
                retdata.error_msg = serializer.errors["ai_skill_url"][0]
            return Response(retdata.result)

        ai_skill_id = serializer.validated_data.get("ai_skill_id")
        name = serializer.validated_data.get("name")
        description = serializer.validated_data.get("description")
        ai_skill_url = serializer.validated_data.get("ai_skill_url")
        if not ai_skill_id:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="AI技能接口ID是必须的"
            )
            return Response(retdata.result)
        if not name and not description and not ai_skill_url:
            retdata = BaseResponse(code=0, msg="error", error_msg="请传入须修改的数据")
            return Response(retdata.result)

        ai_skill = ai_skills.filter(ai_skill_id=ai_skill_id).first()
        if not ai_skill:
            retdata = BaseResponse(code=0, msg="error", error_msg="AI技能接口不存在")
            return Response(retdata.result)

        if ai_skill.bound:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="技能被摄像头绑定，请解绑后修改接口信息"
            )
            return Response(retdata.result)

        new_ai_skill_obj = serializer.save()
        retdata = BaseResponse(
            code=1,
            msg="success",
            success_msg="AI技能接口信息更新成功",
            data=InterfaceSerializer(new_ai_skill_obj).data,
        )
        return Response(retdata.result)


class DeleteInterface(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        serializer = InterfaceIDSerializer(data=request.data)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_id"):
                if serializer.errors["ai_skill_id"][0].code == "required":
                    retdata.error_msg = "技能接口ID是必须的"
                else:
                    retdata.error_msg = "技能接口ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        ai_skill = AISkill.objects.filter(
            user=request.user,
            ai_skill_id=serializer.validated_data["ai_skill_id"],
        ).first()
        if not ai_skill:
            retdata = BaseResponse(code=0, msg="error", error_msg="AI技能接口不存在")
            return Response(retdata.result)

        if ai_skill.bound:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="技能被摄像头绑定，请解绑后删除"
            )
            return Response(retdata.result)

        ai_skill.delete()
        retdata = BaseResponse(code=1, msg="success", success_msg="AI技能接口删除成功")
        return Response(retdata.result)


class RefreshState(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kargs):
        serializer = InterfaceIDSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("ai_skill_id"):
                if serializer.errors["ai_skill_id"][0].code == "required":
                    retdata.error_msg = "技能接口ID是必须的"
                else:
                    retdata.error_msg = "技能接口ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        ai_skill = AISkill.objects.filter(
            user=request.user,
            ai_skill_id=serializer.validated_data.get("ai_skill_id"),
        ).first()

        try:
            ai_skill_test = requests.get(
                ai_skill.ai_skill_url, timeout=10
            ).status_code
            if ai_skill_test != 200:
                ai_skill.state = 0
                ai_skill.save()
                retdata = BaseResponse(
                    code=1, msg="success", success_msg="接口异常", data=0
                )
                return Response(retdata.result)
            else:
                ai_skill.state = 1
                ai_skill.save()
                retdata = BaseResponse(
                    code=1, msg="success", success_msg="接口正常", data=1
                )
                return Response(retdata.result)

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout,
        ):
            ai_skill.state = 0
            ai_skill.save()
            retdata = BaseResponse(
                code=1, msg="success", success_msg="接口异常", data=0
            )
            return Response(retdata.result)
