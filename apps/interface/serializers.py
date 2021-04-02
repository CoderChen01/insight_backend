import re

from rest_framework import serializers
import requests

from .models import AISkillGroup, AISkill
from rest_tools.id_validator import id_validator


class InterfaceGroupIDSerializer(serializers.Serializer):
    ai_skill_group_id = serializers.CharField(max_length=50, validators=[id_validator, ])


class InterfaceIDSerializer(serializers.Serializer):
    ai_skill_id = serializers.CharField(max_length=50, validators=[id_validator, ])


class InterfaceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISkillGroup
        fields = (
            'ai_skill_group_id',
            'name',
            'description',
            'add_time'
        )
        extra_kwargs = {
            'ai_skill_group_id': {
                'validators': [id_validator, ]
            },
            'add_time': {
                'format': '%Y-%m-%d %H:%M:%S',
                'read_only': True
            }
        }

    def create(self, validated_data):
        return AISkillGroup.objects.create(**validated_data)

    def update(self, instance, validated_data):
        ai_skill_group = instance.filter(ai_skill_group_id=validated_data.pop('ai_skill_group_id')).first()
        ai_skill_group.name = validated_data.get('name', ai_skill_group.name)
        ai_skill_group.description = validated_data.get('description', ai_skill_group.description)
        ai_skill_group.save()
        return ai_skill_group


class InterfaceSerializer(serializers.ModelSerializer):
    ai_skill_group_id = serializers.CharField(
        max_length=50,
        validators=[id_validator, ],
        write_only=True
    )

    class Meta:
        model = AISkill
        fields = (
            'ai_skill_id',
            'ai_skill_group_id',
            'name',
            'description',
            'ai_skill_url',
            'state',
            'add_time'
        )
        extra_kwargs = {
            'state': {
                'read_only': True,
                'source': 'get_state_display'
            },
            'add_time': {
                'format': '%Y-%m-%d %H-%M-%S',
                'read_only': True
            },
            'ai_skill_id': {
                'validators': [id_validator, ]
            }
        }

    def validate_ai_skill_url(self, value):
        pattern = re.compile(r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$')
        if not pattern.search(value):
            raise serializers.ValidationError('URL格式错误')

        try:
            ai_skill_test = requests.get(value, timeout=10).status_code
            if ai_skill_test != 200:
                raise serializers.ValidationError('接口无法访问')
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
            raise serializers.ValidationError('接口无法访问')

        return value

    def create(self, validated_data):
        ai_skill_group = AISkillGroup.objects.filter(
            user=validated_data['user'],
            ai_skill_group_id=validated_data.pop('ai_skill_group_id')
        ).first()

        return AISkill.objects.create(
            group=ai_skill_group,
            state=1,
            **validated_data
        )


class UpdateInterfaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISkill
        fields = (
            'ai_skill_id',
            'name',
            'description',
            'ai_skill_url',
        )
        extra_kwargs = {
            'ai_skill_id': {
                'validators': [id_validator, ]
            }
        }

    def validate_ai_skill_url(self, value):
        pattern = re.compile(r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$')
        if not pattern.search(value):
            raise serializers.ValidationError('URL格式错误')

        try:
            ai_skill_test = requests.get(value, timeout=10).status_code
            if ai_skill_test != 200:
                raise serializers.ValidationError('接口无法访问')
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout):
            raise serializers.ValidationError('接口无法访问')
        return value

    def update(self, instance, validated_data):
        ai_skill = instance.filter(ai_skill_id=validated_data.pop('ai_skill_id')).first()
        ai_skill.name = validated_data.get('name', ai_skill.name)
        ai_skill.description = validated_data.get('description', ai_skill.description)
        ai_skill_url = validated_data.get('ai_skill_url')

        if ai_skill_url:
            ai_skill.state = 1
            ai_skill.ai_skill_url = ai_skill_url

        ai_skill.save()
        return ai_skill
