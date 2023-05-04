from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_tools.base_responses import BaseResponse
from rest_tools.face_detection.face_detection import FaceDetection

from .models import Face, FaceGroup
from .serializers import (
    FaceGroupIDSerialzier,
    FaceGroupSerializer,
    FaceIDSerializer,
    FaceSerializer,
    UpdateFaceSerializer,
)

__all__ = [
    "CreateFaceGroup",
    "RetrieveFaceGroup",
    "UpdateFaceGroup",
    "DeleteFaceGroup",
    "CreateFace",
    "RetrieveFace",
    "UpdateFace",
    "DeleteFace",
]


class CreateFaceGroup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = FaceGroupSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_group_id"):
                if serializer.errors["face_group_id"][0].code == "required":
                    retdata.error_msg = "人脸库ID是必须的"
                else:
                    retdata.error_msg = "人脸库ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("name"):
                if serializer.errors["name"][0].code == "required":
                    retdata.error_msg = "人脸库名称是必须的"
                else:
                    retdata.error_msg = "人脸库名称不得超过30个字符或为空"
            elif serializer.errors.get("description"):
                retdata.error_msg = "人脸库描述不得超过300个字符"
            return Response(retdata.result)

        has_face_group = FaceGroup.objects.filter(
            user=request.user,
            face_group_id=serializer.validated_data["face_group_id"],
        ).first()
        if has_face_group:
            retdata = BaseResponse(code=0, msg="error", error_msg="人脸库已存在")
            return Response(retdata.result)

        face_group_obj = serializer.save(user=request.user)

        retdata = BaseResponse(
            code=1,
            msg="success",
            data=FaceGroupSerializer(face_group_obj).data,
            success_msg="创建人脸库成功",
        )
        return Response(retdata.result)

    def get(self, request, *args, **kwargs):
        serializer = FaceGroupIDSerialzier(data=request.query_params)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_group_id"):
                if serializer.errors["face_group_id"][0].code == "required":
                    retdata.error_msg = "人脸库ID是必须的"
                else:
                    retdata.error_msg = "人脸库ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        has_face_group = FaceGroup.objects.filter(
            user=request.user,
            face_group_id=serializer.validated_data["face_group_id"],
        ).first()

        if has_face_group:
            retdata = BaseResponse(
                code=1, msg="success", data=1, success_msg="人脸库已存在"
            )
            return Response(retdata.result)
        else:
            retdata = BaseResponse(
                code=1, msg="success", data=0, success_msg="人脸库不存在，可创建"
            )
            return Response(retdata.result)


class RetrieveFaceGroup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        face_groups = FaceGroup.objects.filter(user=request.user)
        serializer = FaceGroupSerializer(face_groups, many=True)

        retdata = BaseResponse(
            code=1,
            msg="success",
            success_msg="人脸库数据请求成功",
            data=serializer.data,
        )
        return Response(retdata.result)


class UpdateFaceGroup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        face_groups = FaceGroup.objects.filter(user=request.user)
        serializer = FaceGroupSerializer(
            instance=face_groups, data=request.data, partial=True
        )

        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_group_id"):
                retdata.error_msg = "人脸库ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("name"):
                retdata.error_msg = "人脸库名称不得超过30个字符或为空"
            elif serializer.errors.get("description"):
                retdata.error_msg = "人脸库描述不得超过300个字符"
            return Response(retdata.result)

        face_group_id = serializer.validated_data.get("face_group_id")
        name = serializer.validated_data.get("name")
        description = serializer.validated_data.get("description")
        if not name and not description:
            retdata = BaseResponse(code=0, msg="error", error_msg="请传入须修改数据")
            return Response(retdata.result)

        if not face_group_id:
            retdata = BaseResponse(code=0, msg="error", error_msg="必须传入分组ID")
            return Response(retdata.result)

        face_group = FaceGroup.objects.filter(
            user=request.user, face_group_id=face_group_id
        ).first()
        if not face_group:
            retdata = BaseResponse(code=0, msg="error", error_msg="无指定人脸库")
            return Response(retdata.result)

        if face_group.bound:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="人脸库已绑定摄像头，请先解除绑定后修改信息"
            )
            return Response(retdata.result)

        new_face_group_obj = serializer.save()
        retdata = BaseResponse(
            code=1,
            msg="success",
            data=FaceGroupSerializer(new_face_group_obj).data,
            success_msg="人脸库信息修改成功",
        )
        return Response(retdata.result)


class DeleteFaceGroup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        serializer = FaceGroupIDSerialzier(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_group_id"):
                if serializer.errors["face_group_id"][0].code == "required":
                    retdata.error_msg = "人脸库ID是必须的"
                else:
                    retdata.error_msg = "人脸库ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        face_group = FaceGroup.objects.filter(
            user=request.user,
            face_group_id=serializer.validated_data["face_group_id"],
        ).first()
        if not face_group:
            retdata = BaseResponse(code=0, msg="error", error_msg="不存在该人脸库")
            return Response(retdata.result)

        if face_group.bound:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="人脸库已绑定摄像头，请先解除绑定后删除"
            )
            return Response(retdata.result)

        face_group.delete()
        retdata = BaseResponse(code=1, msg="success", success_msg="删除人脸库成功")
        return Response(retdata.result)


class CreateFace(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = FaceSerializer(data=request.data)

        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_id"):
                if serializer.errors["face_id"][0].code == "required":
                    retdata.error_msg = "人脸ID是必须的"
                else:
                    retdata.error_msg = "人脸ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("face_group_id"):
                if serializer.errors["face_group_id"][0].code == "required":
                    retdata.error_msg = "人脸库ID是必须的"
                else:
                    retdata.error_msg = "人脸库ID不合法，为6-20位字母、数字或下划线"
            elif serializer.errors.get("name"):
                if serializer.errors["name"][0].code == "required":
                    retdata.error_msg = "人脸名称是必须的"
                else:
                    retdata.error_msg = "人脸名称不得超过30个字符或为空"
            elif serializer.errors.get("face_image"):
                if serializer.errors["face_image"][0].code == "required":
                    retdata.error_msg = "人脸图片base64编码是必须的"
                else:
                    retdata.error_msg = "请上传一个有效的图片文件"
            return Response(retdata.result)

        has_face = Face.objects.filter(
            user=request.user, face_id=serializer.validated_data["face_id"]
        ).first()
        if has_face:
            retdata = BaseResponse(code=0, msg="error", error_msg="人脸已存在")
            return Response(retdata.result)

        has_face_group_id = FaceGroup.objects.filter(
            user=request.user,
            face_group_id=serializer.validated_data["face_group_id"],
        ).first()
        if not has_face_group_id:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="人脸库不存在，无法绑定人脸"
            )
            return Response(retdata.result)

        face_img_b64 = request.data.get("face_image")
        face_detector = FaceDetection(image=face_img_b64)
        if not face_detector.detect():
            retdata = BaseResponse(
                code=0, msg="error", error_msg="图片中没有人脸或非标准人脸照片"
            )
            return Response(retdata.result)

        face_obj = serializer.save(user=request.user)
        redata = BaseResponse(
            code=1,
            msg="success",
            data=FaceSerializer(face_obj).data,
            success_msg="人脸添加成功",
        )
        return Response(redata.result)

    def get(self, request, *args, **kwargs):
        serializer = FaceIDSerializer(data=request.query_params)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_id"):
                if serializer.errors["face_id"][0].code == "required":
                    retdata.error_msg = "人脸ID是必须的"
                else:
                    retdata.error_msg = "人脸ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        has_face = Face.objects.filter(
            user=request.user, face_id=serializer.validated_data["face_id"]
        )
        retdata = BaseResponse(code=1, msg="successs")
        if not has_face:
            retdata.success_msg = "人脸不存在，可创建"
            retdata.data = 0
        else:
            retdata.success_msg = "人脸已存在"
            retdata.data = 1

        return Response(retdata.result)


class RetrieveFace(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = FaceGroupIDSerialzier(data=request.query_params)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_group_id"):
                if serializer.errors["face_group_id"][0].code == "required":
                    retdata.error_msg = "人脸库ID是必须的"
                else:
                    retdata.error_msg = "人脸库ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        face_group = FaceGroup.objects.filter(
            user=request.user,
            face_group_id=serializer.validated_data["face_group_id"],
        ).first()
        if not face_group:
            retdata = BaseResponse(code=0, msg="error", error_msg="人脸库不存在")
            return Response(retdata.result)

        faces = face_group.face_set.all()
        face_serializer = FaceSerializer(faces, many=True)
        retdata = BaseResponse(
            code=1,
            msg="success",
            success_msg="数据请求成功",
            data=face_serializer.data,
        )
        return Response(retdata.result)


class UpdateFace(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        faces = Face.objects.filter(user=request.user)
        serializer = UpdateFaceSerializer(
            instance=faces, data=request.data, partial=True
        )
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_id"):
                retdata.error_msg = "人脸库ID，为6-20位字母、数字或下划线"
            elif serializer.errors.get("name"):
                retdata.error_msg = "人脸名称不能超过30个字符或为空"
            elif serializer.errors.get("face_image"):
                retdata.error_msg = "请上传一个有效的图片文件"
            return Response(retdata.result)

        face_id = serializer.validated_data.get("face_id")
        name = serializer.validated_data.get("name")
        face_image = serializer.validated_data.get("face_image")
        if not name and not face_image:
            retdata = BaseResponse(code=0, msg="error", error_msg="请传入须修改数据")
            return Response(retdata.result)
        if not face_id:
            retdata = BaseResponse(code=0, msg="error", error_msg="人脸ID是必须的")
            return Response(retdata.result)

        face = faces.filter(face_id=face_id).first()
        if not face:
            retdata = BaseResponse(code=0, msg="error", error_msg="不存在该人脸")
            return Response(retdata.result)

        if face.group.bound:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="所属人脸库已绑定摄像头，请先解除绑定后修改人脸信息"
            )
            return Response(retdata.result)

        face_image = request.data.get("face_image")
        if face_image:
            face_detector = FaceDetection(image=face_image)
            if not face_detector.detect():
                retdata = BaseResponse(
                    code=0, msg="error", error_msg="图片中没有人脸或非标准人脸照片"
                )
                return Response(retdata.result)

        new_face_obj = serializer.save()
        retdata = BaseResponse(
            code=1,
            msg="success",
            data=FaceSerializer(new_face_obj).data,
            success_msg="人脸信息更改成功",
        )
        return Response(retdata.result)


class DeleteFace(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        serializer = FaceIDSerializer(data=request.data)
        if not serializer.is_valid():
            retdata = BaseResponse(code=0, msg="error")
            if serializer.errors.get("face_id"):
                if serializer.errors["face_id"][0].code == "required":
                    retdata.error_msg = "人脸ID是必须的"
                else:
                    retdata.error_msg = "人脸ID不合法，为6-20位字母、数字或下划线"
            return Response(retdata.result)

        face = Face.objects.filter(
            user=request.user, face_id=serializer.validated_data["face_id"]
        ).first()
        if not face:
            retdata = BaseResponse(code=0, msg="error", error_msg="不存在人脸")
            return Response(retdata.result)

        if face.group.bound:
            retdata = BaseResponse(
                code=0, msg="error", error_msg="人脸所属组绑定了技能，不能删除"
            )
            return Response(retdata.result)

        face.face_image.delete()
        face.delete()
        retdata = BaseResponse(code=1, msg="success", success_msg="人脸信息删除成功")
        return Response(retdata.result)
