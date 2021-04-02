from rest_framework import serializers

from .models import Incident
from camera.models import Camera
from interface.models import AISkill
from rest_tools.id_validator import id_validator
from rest_tools.base64_image_field import Base64ImageField


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = (
            'name',
        )
        read_only_fields = fields


class AISkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISkill
        fields = (
            'name',
        )
        read_only_fields = fields


class IncidentSrializer(serializers.ModelSerializer):
    camera = CameraSerializer()
    ai_skill = AISkillSerializer()
    incident_image = Base64ImageField(represent_in_base64=True)
    class Meta:
        model = Incident
        fields = (
            'incident_id',
            'incident_image',
            'camera',
            'ai_skill',
            'response',
            'occurrence_time'
        )
        read_only_fields = fields
        extra_kwargs = {
            'incident_id': {
                'validators': [id_validator, ]
            },
            'occurrence_time': {
                'format': '%Y-%m-%d %H:%M:%S'
            }
        }


class RetrieveIncidentSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50, validators=[id_validator, ], required=False)
    ai_skill_id = serializers.CharField(max_length=50, validators=[id_validator, ], required=False)
    time_range = serializers.JSONField(required=False)
    offset = serializers.IntegerField(min_value=0)
    limit = serializers.IntegerField(min_value=0)

    def validate_time_range(self, value):
        if value:
            fields = (
                'start_time',
                'end_time'
            )
            if len(value) != len(fields):
                raise serializers.ValidationError('缺少或多于参数')

            for field in value:
                if field not in fields:
                    raise serializers.ValidationError('time_range只能有start_time与end_time两个键')

            if value[fields[0]] > value[fields[1]]:
                raise serializers.ValidationError('start_time须小于等于end_time')

            return value

        return value


class IncidentIDSerializer(serializers.Serializer):
    incident_id = serializers.UUIDField()


class DeleteAllIncidentsSerilizer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=50, validators=[id_validator, ], required=False)
    ai_skill_id = serializers.CharField(max_length=50, validators=[id_validator, ], required=False)
    time_range = serializers.JSONField(required=False)

    def validate_time_range(self, value):
        if value:
            fields = (
                'start_time',
                'end_time'
            )
            if len(value) != len(fields):
                raise serializers.ValidationError('缺少或多于参数')

            for field in value:
                if field not in fields:
                    raise serializers.ValidationError('time_range只能有start_time与end_time两个键')

            if value[fields[0]] > value[fields[1]]:
                raise serializers.ValidationError('start_time须小于等于end_time')

            return value

        return value
