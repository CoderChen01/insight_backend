import json

from rest_framework import serializers

from .models import *
from face.models import FaceGroup
from interface.models import AISkill
from rest_tools.id_validator import id_validator
from rest_tools.extract_frame_utils import is_opened


__all__ = [
    'HasCameraGroupSerializer',
    'CreateCameraGroupSerializer',
    'RetrieveCameraGroupSerializer',
    'UpdateCameraGroupSerializer',
    'DeleteCameraGroupSerializer',
    'HasCameraSerializer',
    'CreateCameraSerializer',
    'RetrieveCameraCheckSerializer',
    'RetrieveCameraSerializer',
    'UpdateCameraSerializer',
    'DeleteCameraSerializer',
    'CameraPreviewSerializer',
    'SetExtractFrameSettingsSerializer',
    'SetAISkillSettingsSerializer',
    'StartSerializer',
    'StopSerializer',
    'PauseSerializer',
    'RestartSerializer'
]


class HasCameraGroupSerializer(serializers.Serializer):
    camera_group_id = serializers.CharField(max_length=50, validators=[id_validator,])


class CreateCameraGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraGroup
        fields = (
            'camera_group_id',
            'name',
            'description',
            'add_time'
        )
        read_only_fields = ('add_time', )
        extra_kwargs = {
            'camera_group_id': {
                'validators': [id_validator,]
            }
        }

    def create(self, validated_data):
        return CameraGroup.objects.create(**validated_data)


class RetrieveCameraGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraGroup
        fields = ('name', 'camera_group_id', 'description', 'add_time')
        read_only_fields = fields
        extra_kwargs = {
            'add_time': {
                'format': '%Y-%m-%d %H:%M:%S'
            }
        }


class UpdateCameraGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraGroup
        fields = (
            'name',
            'camera_group_id',
            'description'
        )
        extra_kwargs = {
            'name': {
                'required': False,
                'write_only': True
            },
            'camera_group_id': {
                'write_only': True,
                'validators': [id_validator,]
            },
            'description': {
                'required': False,
                'write_only': True
            }
        }


class DeleteCameraGroupSerializer(serializers.Serializer):
     camera_group_id = serializers.CharField(max_length=50, validators=[id_validator, ])
     force = serializers.BooleanField(default=False)


class HasCameraSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50, validators=[id_validator, ])


class CreateCameraSerializer(serializers.ModelSerializer):
    """camera model serializer"""
    camera_group_id = serializers.CharField(max_length=50, validators=[id_validator, ])
    class Meta:
        model = Camera
        fields = (
            'camera_id',
            'camera_group_id',
            'name',
            'description',
            'camera_url'
        )
        extra_kwargs = {
            'camera_id': {
                'validators': [id_validator, ]
            }
        }

    def validate_camera_url(self, value):
        if not value.startswith('rtsp://') and not value.startswith('rtmp://'):
            raise serializers.ValidationError('摄像头视频流地址不合法，只支持RTSP或RTMP')

        if not is_opened(value):
            raise serializers.ValidationError('视频流无法访问')
        return value

    def create(self, validated_data):
        """create camera base info"""
        camera_group = CameraGroup.objects.filter(
            user=validated_data['user'],
            camera_group_id=validated_data.pop('camera_group_id')
        ).first()
        return Camera.objects.create(
            state=11,
            group=camera_group,
            **validated_data
        )


class RetrieveCameraCheckSerializer(serializers.Serializer):
    camera_group_id = serializers.CharField(max_length=50,
                                            validators=[id_validator, ],
                                            write_only=True)


class AISkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISkill
        fields = (
            'ai_skill_id',
            'name',
            'description',
            'ai_skill_url',
            'state'
        )
        read_only_fields = fields
        extra_kwargs = {
            'state': {
                'source': 'get_state_display'
            }
        }


class FaceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceGroup
        fields = (
            'face_group_id',
        )
        read_only_fields = fields


class FaceSettingsSerializer(serializers.ModelSerializer):
    face_group = FaceGroupSerializer(many=True)
    class Meta:
        model = FaceSettings
        fields = (
            'face_group',
            'similarity',
            'quality'
        )
        read_only_fields = fields


class AISkillSettingsSerializer(serializers.ModelSerializer):
    ai_skill = AISkillSerializer()
    face_relevance = FaceSettingsSerializer()
    class Meta:
        model = AISkillSettings
        fields = (
            'ai_skill',
            'coordinates',
            'face_relevance'
        )
        read_only_fields = fields


class ExtractionSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraExtractionSettings
        fields = (
            'frequency',
            'start_time',
            'end_time'
        )
        read_only_fields = fields


class RetrieveCameraSerializer(serializers.ModelSerializer):
    ai_skill_settings = AISkillSettingsSerializer(many=True)
    extraction_settings = ExtractionSettingsSerializer()
    class Meta:
        model = Camera
        exclude = ('user', 'id', 'group')
        read_only_fields = (
            'ai_skill_settings',
            'extraction_settings',
            'camera_id',
            'name',
            'description',
            'camera_url',
            'state',
            'add_time'
        )
        extra_kwargs = {
            'add_time': {'format': '%Y-%m-%d %H:%M:%S'},
            'state': {'source': 'get_state_display'}
        }


class UpdateCameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = (
            'camera_id',
            'name',
            'description',
            'camera_url'
        )
        extra_kwargs = {
            'camera_id': {'validators': [id_validator, ]},
            'name': {'required': False},
            'descritpion': {'required': False},
            'camera_url': {'required': False}
        }

    def validate_camera_url(self, value):
        if not value.startswith('rtsp://') and not value.startswith('rtmp://'):
            raise serializers.ValidationError('摄像头视频流地址不合法，只支持RTSP或RTMP')

        if not is_opened(value):
            raise serializers.ValidationError('视频流无法访问')
        return value


class DeleteCameraSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50,validators=[id_validator, ])
    force = serializers.BooleanField(default=False)


class CameraPreviewSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50,validators=[id_validator, ])


class SetExtractFrameSettingsSerializer(serializers.ModelSerializer):
    camera_id = serializers.CharField(max_length=50,validators=[id_validator, ])

    class Meta:
        model = CameraExtractionSettings
        fields = (
            'camera_id',
            'frequency',
            'start_time',
            'end_time'
        )
        extra_kwargs = {
            'start_time': {
                'format': '%H:%M'
            },
            'end_time': {
                'format': '%H:%M'
            }
        }

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError('开始时间需要小于结束时间')
        return attrs

    def create(self, validated_data):
        camera_obj = Camera.objects.filter(user=validated_data.pop('user'),
                              camera_id=validated_data.pop('camera_id')).first()
        old_extraction_settings = camera_obj.extraction_settings
        extraction_settings = CameraExtractionSettings.objects.create(**validated_data)

        if not old_extraction_settings:
            camera_obj.state = 12  # first set extraction settings

        camera_obj.extraction_settings = extraction_settings
        camera_obj.save()
        if old_extraction_settings:
            old_extraction_settings.delete()
        return camera_obj


class SetAISkillSettingsSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50,validators=[id_validator, ])
    ai_skill_settings = serializers.ListField(
        child=serializers.JSONField(),
        max_length=25,
        allow_empty=True
    )

    def validate_ai_skill_settings(self, value):
        if value:
            fields = (
                'ai_skill_id',
                'face_relevance',
                'coordinates'
            )

            for ai_skill_setting in value:
                if len(ai_skill_setting) < 2 or len(ai_skill_setting) > 3:
                    raise serializers.ValidationError('AI技能设置缺少参数')

                if fields[0] not in ai_skill_setting:
                    raise serializers.ValidationError('AI技能ID是必须的')
                elif not isinstance(ai_skill_setting[fields[0]], str):
                    raise serializers.ValidationError('AI技能ID为字符串类型')
                else:
                    try:
                        id_validator(ai_skill_setting[fields[0]])
                    except serializers.ValidationError:
                        raise serializers.ValidationError('AI技能ID不合法，为6-20为字母、数字或下划线')


                face_relevance = ai_skill_setting.get(fields[1])
                if face_relevance:
                    face_fields = (
                        'face_groups_id',
                        'similarity',
                        'quality'
                    )
                    if len(face_relevance) != len(face_fields):
                        raise serializers.ValidationError('人脸库绑定设置缺少必要参数或存在不必要参数')

                    for face_field in face_relevance:
                        if face_field not in face_fields:
                            raise serializers.ValidationError('人脸库绑定设置存在不必要的参数' + face_field)

                    if not isinstance(face_relevance[face_fields[0]], list):
                        raise serializers.ValidationError('face_groups_id字段为列表类型')
                    else:
                        for face_group_id in face_relevance[face_fields[0]]:
                            if not isinstance(face_group_id, str):
                                raise serializers.ValidationError('人脸库ID是字符串类型')

                            try:
                                id_validator(face_group_id)
                            except serializers.ValidationError:
                                raise serializers.ValidationError('人脸库ID不合法，为6-20为字母、数字或下划线')

                    if not isinstance(face_relevance[face_fields[1]], float):
                        raise serializers.ValidationError('similarity字段必须是浮点型')
                    elif not 0 <= face_relevance[face_fields[1]] <= 1:
                        raise serializers.ValidationError('similarity范围在0-1之间')

                    if not isinstance(face_relevance[face_fields[2]], int):
                        raise serializers.ValidationError('quality字段必须是整型，且只能为0,1,2,3')
                    elif face_relevance[face_fields[2]] not in (0, 1, 2, 3):
                        raise serializers.ValidationError('quality字段只能是0,1,2,3中的一个，分别表示无，低，中，高')

                coordinates = ai_skill_setting.get(fields[2])
                if not coordinates:
                    raise serializers.ValidationError('图像分析区域是必须的')
                else:
                    coordinates_fields = (
                        'x_min',
                        'y_min',
                        'x_max',
                        'y_max'
                    )
                    if len(coordinates) != len(coordinates_fields):
                        raise serializers.ValidationError('图像分析区域缺少必要参数或存在不必要参数')

                    for coordinates_field in coordinates:
                        if not coordinates_field in coordinates_fields:
                            raise serializers.ValidationError('图像分析区域存在多于参数' + coordinates_field)

                        if not isinstance(coordinates[coordinates_field], int):
                            raise serializers.ValidationError('坐标都是整型')

                    if coordinates[coordinates_fields[2]] <= coordinates[coordinates_fields[0]]:
                        raise serializers.ValidationError('x_max应该大于x_min')

                    if coordinates[coordinates_fields[3]] <= coordinates[coordinates_fields[1]]:
                        raise serializers.ValidationError('y_max应该大于y_min')

                for field in ai_skill_setting:
                    if field not in fields:
                        raise serializers.ValidationError('AI技能配置存在不必要的参数' + field)

            return value
        return value

    def create(self, validated_data):
        user = validated_data.pop('user')

        camera_obj = Camera.objects.filter(
            user=user,
            camera_id=validated_data.pop('camera_id')
        ).first()

        # delete old settings for overriding the settings
        old_ai_skill_settings = camera_obj.ai_skill_settings.all()
        if old_ai_skill_settings:
            for old_ai_skill_setting in old_ai_skill_settings:
                old_ai_skill_setting.ai_skill.bound = False
                old_ai_skill_setting.ai_skill.save()
                face_relevance = old_ai_skill_setting.face_relevance
                if face_relevance:
                    face_groups = face_relevance.face_group.all()
                    if face_groups:
                        for face_group in face_groups:
                            face_group.bound = False
                            face_group.save()
                    face_relevance.face_group.clear()
                    face_relevance.delete()
                old_ai_skill_setting.delete()
            camera_obj.ai_skill_settings.clear()
        else:
            camera_obj.state = 13  # first set AI skill settings
        camera_obj.save()

        ai_skill_settings = validated_data['ai_skill_settings']
        if ai_skill_settings:
            ai_settings = []
            for ai_skill_setting in ai_skill_settings:
                ai_skill = AISkill.objects.filter(
                    user=user,
                    ai_skill_id=ai_skill_setting['ai_skill_id']
                ).first()
                ai_skill.bound = True
                ai_skill.save()

                face_relevance = ai_skill_setting.get('face_relevance')
                if face_relevance:
                    face_settings = FaceSettings()
                    face_settings.similarity = face_relevance['similarity']
                    face_settings.quality = face_relevance['quality']
                    face_settings.save()

                    for face_group_id in face_relevance['face_groups_id']:
                        face_group = FaceGroup.objects.filter(
                            user=user,
                            face_group_id=face_group_id
                        ).first()
                        face_group.bound = True
                        face_group.save()

                        face_settings.face_group.add(face_group)

                    ai_setting =  AISkillSettings.objects.create(
                        ai_skill=ai_skill,
                        coordinates=json.dumps(ai_skill_setting['coordinates']),
                        face_relevance=face_settings
                    )
                    ai_settings.append(ai_setting)

                else:
                    ai_setting = AISkillSettings.objects.create(
                            ai_skill=ai_skill,
                            coordinates=json.dumps(ai_skill_setting['coordinates'])
                        )
                    ai_settings.append(ai_setting)

            camera_obj.ai_skill_settings.set(ai_settings)
        else:
            camera_obj.ai_skill_settings.clear()
            camera_obj.state = 12
            camera_obj.save()

        return camera_obj


class StartSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50, validators=[id_validator, ])


class StopSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50, validators=[id_validator, ])


class PauseSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50, validators=[id_validator, ])


class RestartSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50, validators=[id_validator, ])
