from rest_framework import serializers

from rest_tools.base64_image_field import Base64ImageField
from rest_tools.id_validator import id_validator

from .models import Face, FaceGroup


class FaceGroupIDSerialzier(serializers.Serializer):
    face_group_id = serializers.CharField(
        max_length=50,
        validators=[
            id_validator,
        ],
    )


class FaceIDSerializer(serializers.Serializer):
    face_id = serializers.CharField(
        max_length=50,
        validators=[
            id_validator,
        ],
    )


class FaceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceGroup
        fields = ("face_group_id", "name", "description", "add_time")
        extra_kwargs = {
            "face_group_id": {
                "validators": [
                    id_validator,
                ],
                "required": True,
            },
            "add_time": {"format": "%Y-%m-%d %H:%M:%S", "read_only": True},
        }

    def create(self, validated_data):
        return FaceGroup.objects.create(**validated_data)

    def update(self, instance, validated_data):
        face_group = instance.filter(
            face_group_id=validated_data.pop("face_group_id")
        ).first()
        face_group.name = validated_data.get("name", face_group.name)
        face_group.description = validated_data.get(
            "description", face_group.description
        )
        face_group.save()
        return face_group


class FaceSerializer(serializers.ModelSerializer):
    face_image = Base64ImageField(represent_in_base64=True)
    face_group_id = serializers.CharField(
        validators=[
            id_validator,
        ],
        write_only=True,
    )

    class Meta:
        model = Face
        fields = ("face_id", "face_group_id", "name", "face_image", "add_time")
        extra_kwargs = {
            "face_id": {
                "validators": [
                    id_validator,
                ]
            },
            "add_time": {"format": "%Y-%m-%d %H:%M:%S", "read_only": True},
        }

    def create(self, validated_data):
        face_group = FaceGroup.objects.filter(
            user=validated_data["user"],
            face_group_id=validated_data.pop("face_group_id"),
        ).first()

        return Face.objects.create(group=face_group, **validated_data)


class UpdateFaceSerializer(serializers.ModelSerializer):
    face_image = Base64ImageField(represent_in_base64=True)

    class Meta:
        model = Face
        fields = ("face_id", "name", "face_image")
        extra_kwargs = {
            "face_id": {
                "validators": [
                    id_validator,
                ]
            }
        }

    def update(self, instance, validated_data):
        face = instance.filter(face_id=validated_data.pop("face_id")).first()
        face.name = validated_data.get("name", face.name)
        face_image = validated_data.get("face_image")
        if face_image:
            face.face_image.delete()
            face.face_image = face_image
        face.save()
        return face
