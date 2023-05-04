from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_tools.base_responses import BaseResponse

from .models import Incident
from .serializers import (
    DeleteAllIncidentsSerilizer,
    IncidentIDSerializer,
    IncidentSrializer,
    RetrieveIncidentSerializer,
)


class RetrieveIncident(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = RetrieveIncidentSerializer(data=request.query_params)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("camera_id"):
                retdata.error_msg = "摄像头ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("ai_skill_id"):
                retdata.error_msg = "AI技能接口ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("time_range"):
                retdata.error_msg = "时间范围不合法，须传入start_time和end_time字段"
            elif serializer.errors.get("offset"):
                if serializer.errors["offset"][0].code == "required":
                    retdata.error_msg = "须传入数据偏移量"
                else:
                    retdata.error_msg = "数据偏移量是整型"
            elif serializer.errors.get("limit"):
                if serializer.errors["limit"][0].code == "required":
                    retdata.error_msg = "须传入数据限制量"
                else:
                    retdata.error_msg = "数据限制量为整型"
            return Response(retdata.result)

        camera_id = serializer.validated_data.get("camera_id")
        ai_skill_id = serializer.validated_data.get("ai_skill_id")
        time_range = serializer.validated_data.get("time_range")

        incidents = Incident.objects.filter(user=request.user)
        if not incidents:
            retdata = BaseResponse(
                code=1,
                msg="success",
                data=[],
                all_count=0,
                sucess_msg="暂无任何事件发生",
            )
            return Response(retdata.result)

        if camera_id:
            incidents = incidents.filter(camera__camera_id=camera_id)

        if ai_skill_id:
            incidents = incidents.filter(ai_skill__ai_skill_id=ai_skill_id)

        if time_range:
            incidents = incidents.filter(
                occurrence_time__range=[
                    time_range["start_time"],
                    time_range["end_time"],
                ]
            )

        all_count = incidents.count()
        start = serializer.validated_data["offset"]
        end = start + serializer.validated_data["limit"]

        # the edge
        is_end = False
        if end > all_count:
            end = all_count
            is_end = True

        incidents = incidents[start:end]
        incidents_serializer = IncidentSrializer(incidents, many=True)

        retdata = BaseResponse(
            code=1,
            msg="success",
            success_msg="事件获取成功",
            all_count=all_count,
            is_end=is_end,
            next_offset=end,
            data=incidents_serializer.data,
        )
        return Response(retdata.result)


class DeleteIncident(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, requests, *args, **kwargs):
        serializer = IncidentIDSerializer(data=requests.data)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("incident_id"):
                if serializer.errors["incident_id"][0].code == "required":
                    retdata.error_msg = "事件ID是必须的"
                else:
                    retdata.error_msg = "事件ID不合法，为UUID格式"
            return Response(retdata.result)

        incident = Incident.objects.filter(
            user=requests.user,
            incident_id=serializer.validated_data["incident_id"],
        ).first()
        if not incident:
            retdata = BaseResponse(code=0, msg="error", error_msg="事件不存在")
            return Response(retdata.result)

        incident.delete()
        retdata = BaseResponse(code=1, msg="success", success_msg="事件删除成功")
        return Response(retdata.result)


class DeleteAllIncidents(APIView):
    """
    delete all incidents
    """

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        serializer = DeleteAllIncidentsSerilizer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("camera_id"):
                retdata.error_msg = "摄像头ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("ai_skill_id"):
                retdata.error_msg = "AI技能接口ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("time_range"):
                retdata.error_msg = "时间范围不合法，须传入start_time和end_time字段"
            elif serializer.errors.get("offset"):
                if serializer.errors["offset"][0].code == "required":
                    retdata.error_msg = "须传入数据偏移量"
                else:
                    retdata.error_msg = "数据偏移量是整型"
            elif serializer.errors.get("limit"):
                if serializer.errors["limit"][0].code == "required":
                    retdata.error_msg = "须传入数据限制量"
                else:
                    retdata.error_msg = "数据限制量为整型"
            return Response(retdata.result)

        camera_id = serializer.validated_data.get("camera_id")
        ai_skill_id = serializer.validated_data.get("ai_skill_id")
        time_range = serializer.validated_data.get("time_range")

        incidents = Incident.objects.filter(user=request.user)
        if not incidents:
            retdata = BaseResponse(
                code=1, msg="success", sucess_msg="暂无任何事件发生, 无需删除"
            )
            return Response(retdata.result)

        if camera_id:
            incidents = incidents.filter(camera__camera_id=camera_id)

        if ai_skill_id:
            incidents = incidents.filter(ai_skill__ai_skill_id=ai_skill_id)

        if time_range:
            incidents = incidents.filter(
                occurrence_time__range=[
                    time_range["start_time"],
                    time_range["end_time"],
                ]
            )

        incidents.delete()
        retdata = BaseResponse(code=1, msg="success", success_msg="事件删除成功")
        return Response(retdata.result)
