import json
import datetime

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from rest_tools.base_responses import BaseResponse
from rest_tools.extract_frame_utils import get_preview, is_opened
from .models import CameraGroup, Camera
from interface.models import AISkill
from face.models import FaceGroup
from .serializers import *
from .tasks import dispatch_tasks
from rest_tools.redis_operations import RedisTaskState


__all__ = [
    'CreateCameraGroup',
    'RetrieveCameraGroup',
    'UpdateCameraGroup',
    'DeleteCameraGroup',
    'CreateCamera',
    'RetrieveCamera',
    'UpdateCamera',
    'DeleteCamera',
    'CameraPreview',
    'SetExtractFrameSettings',
    'SetAISkillSettings',
    'Start',
    'Stop'
]


class CreateCameraGroup(APIView):
    """
    add a camera group
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        serializer = HasCameraGroupSerializer(data=request.query_params)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_group_id'):
                if serializer.errors['camera_group_id'][0].code == 'required':
                    retdata.error_msg = '摄像头分组ID是必须的'
                else:
                    retdata.error_msg = '摄像头分组ID不合法，为6-20位字母、数字或下划线'
            return Response(retdata.result)

        camera_group_id = serializer.validated_data.get('camera_group_id')
        has_camera_group = CameraGroup.objects.filter(
            user=request.user,
            camera_group_id=camera_group_id
        ).first()

        if has_camera_group:
            retdata = BaseResponse(
                code=1,
                msg='success',
                data=1,
                success_msg = '组ID已存在'
            )
            return Response(retdata.result)

        retdata = BaseResponse(
            code=1,
            msg='success',
            data=0,
            success_msg='组ID不存在，可新建'
        )
        return Response(retdata.result)

    def post(self, request, *args, **kwargs):
        serializer = CreateCameraGroupSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_group_id'):
                if serializer.errors['camera_group_id'][0].code == 'required':
                    retdata.error_msg = '摄像头分组ID是必须的'
                else:
                    retdata.error_msg = '摄像头分组ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('name'):
                if serializer.errors['name'][0].code == 'required':
                    retdata.error_msg = '摄像头分组名称是必须的'
                else:
                    retdata.error_msg = '摄像头分组名称不能超过30个字符或为空'
            elif serializer.errors.get('description'):
                retdata.error_msg = '摄像头分组描述不能超过300个字符'
            return Response(retdata.result)

        has_camera_group = CameraGroup.objects.filter(
            user=request.user,
            camera_group_id=serializer.validated_data['camera_group_id']
        ).first()

        if has_camera_group:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='分组ID已存在，请重新设置'
            )
            return Response(retdata.result)

        camera_group_obj = serializer.save(user=request.user)
        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='成功创建摄像头分组',
            data=RetrieveCameraGroupSerializer(camera_group_obj).data
        )

        return Response(retdata.result)


class RetrieveCameraGroup(APIView):
    """
    retrive this user's all camera groups.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        camer_groups = CameraGroup.objects.filter(user=request.user)

        data = RetrieveCameraGroupSerializer(camer_groups, many=True)

        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='摄像头组数据请求成功',
            data=data.data
        )

        return Response(retdata.result)


class UpdateCameraGroup(APIView):
    """
    updata camera group
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def patch(self, request, *args, **kwargs):
        serializer = UpdateCameraGroupSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_group_id'):
                if serializer.errors['camera_group_id'][0].code == 'required':
                    retdata.error_msg = '摄像头分组ID是必须的'
                else:
                    retdata.error_msg = '摄像头分组ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('name'):
                retdata.error_msg = '摄像头分组名称不能超过30个字符'
            elif serializer.errors.get('description'):
                retdata.error_msg = '摄像头分组描述不能超过300个字符'
            return Response(retdata.result)

        name = serializer.validated_data.get('name')
        description = serializer.validated_data.get('description')
        if not name and not description:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='请传入须修改参数'
            )
            return Response(retdata.result)

        camera_group = CameraGroup.objects.filter(
            user=request.user,
            camera_group_id=serializer.validated_data['camera_group_id']
        ).first()
        if not camera_group:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='摄像头分组不存在'
            )
            return Response(retdata.result)

        camera_group.name = serializer.validated_data.get('name', camera_group.name)
        camera_group.description = serializer.validated_data.get(
            'description',
             camera_group.description
        )

        camera_group.save()
        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='摄像头组信息修改成功',
            data=RetrieveCameraGroupSerializer(camera_group).data
        )
        return Response(retdata.result)


class DeleteCameraGroup(APIView):
    """
    delete a camera group
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def delete(self, request, *args, **kwargs):
        serializer = DeleteCameraGroupSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_group_id'):
                if serializer.errors['camera_group_id'][0].code == 'required':
                    retdata.error_msg = '摄像头分组ID是必须的'
                else:
                    retdata.error_msg = '摄像头分组ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('force'):
                retdata.error_msg = 'force字段是bool类型'
            return Response(retdata.result)

        camera_group = CameraGroup.objects.filter(
            user=request.user,
            camera_group_id=serializer.validated_data['camera_group_id']
        ).first()
        if not camera_group:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='摄像头分组不存在'
            )
            return Response(retdata.result)

        cameras = camera_group.camera_set.all()
        for camera in cameras:
            if camera.state in (13, 20, 21, 22):
                if serializer.validated_data['force']:
                    for ai_skill_setting in camera.ai_skill_settings.all():
                        ai_skill_setting.ai_skill.bound = False
                        ai_skill_setting.ai_skill.save()
                        face_relevance = ai_skill_setting.face_relevance
                        if face_relevance:
                            for face_group in face_relevance.face_group.all():
                                face_group.bound = False
                                face_group.save()

                    task_id = request.user.username + '##' + camera.camera_id
                    periodic_task = PeriodicTask.objects.filter(
                        name=task_id
                    ).first()
                    if periodic_task:
                        periodic_task.enabled = False
                        periodic_task.save()
                        periodic_task.delete()

                    with RedisTaskState(task_id=task_id) as task_state:
                        task_state.set_state('stopped')

                    camera.ai_skill_settings.clear()

                else:
                    retdata = BaseResponse(
                        code=0,
                        msg='error',
                        error_msg='无法删除摄像头分组，存在摄像头已绑定技能或者正在运行'
                    )
                    return Response(retdata.result)

        camera_group.delete()
        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='摄像头组删除成功'
        )
        return Response(retdata.result)


class CreateCamera(APIView):
    """
    create a camera instance.
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        serializer = HasCameraSerializer(data=request.query_params)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'required':
                    retdata.error_msg = '摄像头ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            return Response(retdata.result)

        camera_id = serializer.validated_data.get('camera_id')
        has_camera = Camera.objects.filter(
            user=request.user,
            camera_id=camera_id
        ).first()

        if has_camera:
            retdata = BaseResponse(
                code=1,
                msg='success',
                data=1,
                success_msg='摄像头ID已存在'
            )
            return Response(retdata.result)

        retdata = BaseResponse(
            code=1,
            msg='success',
            data=0,
            success_msg='摄像头ID不存在，可新建'
        )
        return Response(retdata.result)

    def post(self, request, *args, **kwargs):
        serializer = CreateCameraSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'required':
                    retdata.error_msg = '摄像头ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('camera_group_id'):
                if serializer.errors['camera_group_id'][0].code == 'required':
                    retdata.error_msg = '摄像头分组ID是必须的'
                else:
                    retdata.error_msg = '摄像头分组ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('name'):
                if serializer.errors['name'][0].code == 'required':
                    retdata.error_msg = '摄像头名称是必须的'
                else:
                    retdata.error_msg = '摄像头名称不能超过30个字符或为空'
            elif serializer.errors.get('camera_url'):
                if serializer.errors['camera_url'][0].code == 'required':
                    retdata.error_msg = '摄像头视频流地址是必须的'
                else:
                    retdata.error_msg = serializer.errors['camera_url'][0]
            elif serializer.errors.get('desription'):
                retdata.error_msg = '摄像头描述不能超过300个字符'
            return Response(retdata.result)

        has_camera = Camera.objects.filter(
            user=request.user,
            camera_id=serializer.validated_data['camera_id']
        ).first()
        has_camera_group = CameraGroup.objects.filter(
            user=request.user,
            camera_group_id=serializer.validated_data['camera_group_id']
        ).first()
        if has_camera:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='摄像头ID已存在，请重新设置'
            )
            return Response(retdata.result)

        if not has_camera_group:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='摄像头分组不存在，不可绑定到该分组'
            )
            return Response(retdata.result)

        camera_obj = serializer.save(user=request.user)
        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='摄像头创建成功',
            data=RetrieveCameraSerializer(camera_obj).data
        )

        return Response(retdata.result)


class RetrieveCamera(APIView):
    """
    retrieve Camera data
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        serializer = RetrieveCameraCheckSerializer(data=request.query_params)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_group_id'):
                if serializer.errors['camera_group_id'][0].code == 'required':
                    retdata.error_msg = '摄像头分组ID是必须的'
                else:
                    retdata.error_msg = '摄像头分组ID不合法，为6-20位字母、数字或下划线'
            return Response(retdata.result)

        has_camera_group = CameraGroup.objects.filter(
            camera_group_id=serializer.validated_data['camera_group_id']
        ).first()
        if not has_camera_group:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='没有该摄像头分组'
            )
            return Response(retdata.result)

        cameras = Camera.objects.filter(group__camera_group_id=serializer.validated_data['camera_group_id'])
        cameras_serializer = RetrieveCameraSerializer(instance=cameras, many=True)

        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='数据请求成功',
            data=cameras_serializer.data
        )
        return Response(retdata.result)


class UpdateCamera(APIView):
    """
    update a camera data
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def patch(self, request, *args, **kwargs):
        serializer = UpdateCameraSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'required':
                    retdata.error_msg = '摄像头ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('name'):
                retdata.error_msg = '摄像头名称不能超过30个字符或为空'
            elif serializer.errors.get('description'):
                retdata.error_msg = '摄像头描述不能超过300个字符'
            elif serializer.errors.get('camera_url'):
                retdata.error_msg = serializer.errors['camera_url'][0]
            return Response(retdata.result)

        name = serializer.validated_data.get('name')
        description = serializer.validated_data.get('description')
        camera_url = serializer.validated_data.get('camera_url')
        if not name and not description and not camera_url:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='请传入须修改参数'
            )
            return Response(retdata.result)

        camera_obj = Camera.objects.filter(
            user=request.user,
            camera_id=serializer.validated_data['camera_id']
        ).first()
        if not camera_obj:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='没有该摄像头，请新建'
            )
            return Response(retdata.result)
        if camera_obj.state == 21:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='无法修改摄像头，已绑定技能或者正在运行'
            )
            return Response(retdata.result)

        camera_obj.name = serializer.validated_data.get('name', camera_obj.name)
        camera_obj.description = serializer.validated_data.get('description', camera_obj.description)

        camera_url = serializer.validated_data.get('camera_url')
        if camera_url:
            camera_obj.camera_url = camera_url
            camera_obj.state = 11

        camera_obj.save()
        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='摄像头信息修改成功',
            data=RetrieveCameraSerializer(camera_obj).data
        )
        return Response(retdata.result)


class DeleteCamera(APIView):
    """
    delete a camera data
    """
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def delete(self, request, *args, **kwargs):
        serializer = DeleteCameraSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'requried':
                    retdata.error_msg = '摄像头ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('force'):
                retdata.error_msg = 'force字段是bool类型'
            return Response(retdata.result)

        camera_obj = Camera.objects.filter(
            user=request.user,
            camera_id=serializer.validated_data['camera_id']
        ).first()

        if not camera_obj:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='没有该摄像头'
            )
            return Response(retdata.result)

        if camera_obj.state in (13, 20, 21, 22):
            if serializer.validated_data['force']:
                for ai_skill_setting in camera_obj.ai_skill_settings.all():
                    ai_skill_setting.ai_skill.bound = False
                    ai_skill_setting.ai_skill.save()
                    face_relevances = ai_skill_setting.face_relevance
                    if face_relevances:
                        for face_relevance in face_relevances:
                            face_groups = face_relevance.face_group.all()
                            for face_group in face_groups:
                                face_group.bound = False
                                face_group.save()

                task_id = request.user.username + '##' + camera_obj.camera_id
                periodic_task = PeriodicTask.objects.filter(
                    name=task_id
                ).first()
                if periodic_task:
                    periodic_task.enabled = False
                    periodic_task.save()
                    periodic_task.delete()

                with RedisTaskState(task_id=task_id) as task_state:
                    task_state.set_state('stopped')

                camera_obj.ai_skill_settings.clear()
            else:
                retdata = BaseResponse(
                    code=0,
                    msg='error',
                    error_msg='无法删除摄像头，已绑定技能或者正在运行'
                )
                return Response(retdata.result)

        camera_obj.delete()
        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='删除摄像头成功'
        )
        return Response(retdata.result)


class CameraPreview(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, requests, *args, **kwargs):
        serializer = CameraPreviewSerializer(data=requests.query_params)
        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'required':
                    retdata.error_msg = '摄像图ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            return Response(retdata.result)

        camera = Camera.objects.filter(
            user=requests.user,
            camera_id=serializer.validated_data['camera_id']
        ).first()
        if not camera:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='不存在该摄像头'
            )
            return Response(retdata.result)

        preview = get_preview(camera.camera_url)
        if not preview:
            if not is_opened(camera.camera_url):
                camera.state = 10
                camera.save()

            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='摄像头连接或抽帧发生错误',
                data=RetrieveCameraSerializer(camera).data
            )
            return Response(retdata.result)

        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='摄像头预览图片请求成功',
            data=preview
        )
        return Response(retdata.result)


class SetExtractFrameSettings(APIView):
    """set extracting frame settings"""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = SetExtractFrameSettingsSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'required':
                    retdata.error_msg = '摄像头ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('frequency'):
                if serializer.errors['frequency'][0].code == 'requried':
                    retdata.error_msg = '抽帧频率是必须的'
                else:
                    retdata.error_msg = '抽帧频率只能是1, 2, 3'
            elif serializer.errors.get('start_time'):
                if serializer.errors['start_time'][0].code == 'required':
                    retdata.error_msg = '开始时间是必须的'
                else:
                    retdata.error_msg = '时间格式错误'
            elif serializer.errors.get('end_time'):
                if serializer.errors['end_time'][0].code == 'required':
                    retdata.error_msg = '结束时间是必须的'
                else:
                    retdata.error_msg = '时间格式错误'
            elif serializer.errors.get('non_field_errors'):
                retdata.error_msg = serializer.errors['non_field_errors'][0]
            return Response(retdata.result)

        camera = Camera.objects.filter(
            user=request.user,
            camera_id=serializer.validated_data['camera_id']
        ).first()

        if not camera:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='不存在该摄像头'
            )
            return Response(retdata.result)

        if camera.state == 21:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='摄像头正在运行中，无法设置抽帧配置'
            )
            return Response(retdata.result)

        camera_obj = serializer.save(user=request.user)
        retdata = BaseResponse(
            code=1,
            msg='success',
            data=RetrieveCameraSerializer(camera_obj).data,
            success_msg='抽帧配置成功， 请完成技能配置'
        )
        return Response(retdata.result)


class SetAISkillSettings(APIView):
    """set ai skill settings"""
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = SetAISkillSettingsSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'required':
                    retdata.error_msg = '摄像头ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            elif serializer.errors.get('ai_skill_settings'):
                if serializer.errors['ai_skill_settings'][0].code == 'required':
                    retdata.error_msg = 'AI技能配置是必须的'
                elif serializer.errors['ai_skill_settings'][0].code == 'not_a_list':
                    retdata.error_msg = 'AI技能配置是一个列表类型'
                else:
                    retdata.error_msg = serializer.errors['ai_skill_settings'][0]
            return Response(retdata.result)

        camera_obj = Camera.objects.filter(
            user=request.user,
            camera_id=serializer.validated_data['camera_id']
        ).first()

        if not camera_obj:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='不存在该摄像头'
            )
            return Response(retdata.result)

        if not camera_obj.extraction_settings:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='请先配置抽帧设置'
            )
            return Response(retdata.result)

        if camera_obj.state == 21:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='摄像头正在运行中，无法设置AI技能配置'
            )
            return Response(retdata.result)

        ai_skill_settings = serializer.validated_data['ai_skill_settings']

        for ai_skill_setting in ai_skill_settings:
            has_ai_skill = AISkill.objects.filter(
                user=request.user,
                ai_skill_id=ai_skill_setting['ai_skill_id']
            ).first()
            if not has_ai_skill:
                retdata = BaseResponse(
                    code=0,
                    msg='error',
                    error_msg='配置中含有不存在的AI技能'
                )
                return Response(retdata.result)

            face_relevance = ai_skill_setting.get('face_relevance')
            if face_relevance:
                face_groups_id = face_relevance['face_groups_id']
                for face_group_id in face_groups_id:
                    has_face_group = FaceGroup.objects.filter(
                        user=request.user,
                        face_group_id=face_group_id
                    ).first()

                    if not has_face_group:
                        retdata = BaseResponse(
                            code=0,
                            msg='error',
                            error_msg='配置中含有不存在的人脸库'
                        )
                        return Response(retdata.result)

        camera = serializer.save(user=request.user)
        retdata = BaseResponse(
            code=1,
            msg='success',
            data=RetrieveCameraSerializer(camera).data,
            success_msg='技能配置成功，所有设置配置成功'
        )
        return Response(retdata.result)


class Start(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = StartSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'required':
                    retdata.error_msg = '摄像头ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            return Response(retdata.result)

        camera_obj = Camera.objects.filter(
            user=request.user,
            camera_id=serializer.validated_data['camera_id']
        ).first()

        if not camera_obj:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='没有该摄像头'
            )
            return Response(retdata.result)

        extraction_settings = camera_obj.extraction_settings
        ai_skill_settings = camera_obj.ai_skill_settings.all()

        if not extraction_settings:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='请配置抽帧设置'
            )
            return Response(retdata.result)

        if not ai_skill_settings:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='请配置AI技能配置'
            )
            return Response(retdata.result)

        task_id = request.user.username + '##' + camera_obj.camera_id
        old_periodic_task = PeriodicTask.objects.filter(
            name = task_id
        ).first()
        if old_periodic_task:
            old_periodic_task.enabled = False
            old_periodic_task.save()
            old_periodic_task.delete()
            with RedisTaskState(task_id=task_id) as task_state:
                task_state.set_state('stopped')

        start_time = extraction_settings.start_time
        end_time = extraction_settings.end_time

        # if start_time won't come today, call task utill start_time comes tomorrow
        now_time = datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)
        if end_time > now_time > start_time:
            dispatch_tasks.delay(task_id, end_time.hour, end_time.minute)

        # create the schedule
        minute = '{0}'.format(start_time.minute)
        hour = '{0}'.format(start_time.hour)
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_month='*',
            day_of_week='*',
            month_of_year='*',
            timezone='Asia/Shanghai'
        )

        task_id = request.user.username + '##' + serializer.validated_data['camera_id']
        PeriodicTask.objects.create(
            crontab=schedule,
            name=task_id,
            task='camera.tasks.dispatch_tasks',
            args=json.dumps([task_id, end_time.hour, end_time.minute]),
        )

        camera_obj.state = 21
        camera_obj.save()

        retdata = BaseResponse(
            code=1,
            msg='success',
            success_msg='开始运行',
            data= RetrieveCameraSerializer(camera_obj).data
        )
        return Response(retdata.result)


class Stop(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        serializer = StopSerializer(data=request.data)
        if not serializer.is_valid():
            retdata = BaseResponse(
                code=0,
                msg='error'
            )
            if serializer.errors.get('camera_id'):
                if serializer.errors['camera_id'][0].code == 'required':
                    retdata.error_msg = '摄像头ID是必须的'
                else:
                    retdata.error_msg = '摄像头ID不合法，为6-20位字母、数字或下划线'
            return Response(retdata.result)

        camera_obj = Camera.objects.filter(
            user=request.user,
            camera_id=serializer.validated_data['camera_id']
        ).first()
        if not camera_obj:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='不存在该摄像头'
            )
            return Response(retdata.result)

        task_id = request.user.username + '##' + serializer.validated_data['camera_id']
        periodic_task = PeriodicTask.objects.filter(name=task_id).first()

        if not periodic_task:
            retdata = BaseResponse(
                code=0,
                msg='error',
                error_msg='摄像头没有运行任务'
            )
            return Response(retdata.result)

        periodic_task.enabled = False
        periodic_task.save()
        periodic_task.delete()

        with RedisTaskState(task_id=task_id) as task_state:
            task_state.set_state('stopped')

        camera_obj.state = 22
        camera_obj.save()

        retdata = BaseResponse(
            code=1,
            msg='success',
            data=RetrieveCameraSerializer(camera_obj).data,
            success_msg='任务已结束'
        )
        return Response(retdata.result)
