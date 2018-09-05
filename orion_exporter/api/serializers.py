from orion_exporter.models import OrionEntity
from orion_exporter.models import OrionServicePath
from rest_framework import serializers


class OrionServicePathSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrionServicePath
        exclude = []


class OrionServicePathNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrionServicePath
        exclude = ['entity']


class OrionEntitySerializer(serializers.ModelSerializer):
    service_paths = OrionServicePathNestedSerializer(source='entity', read_only=True, many=True)

    class Meta:
        model = OrionEntity
        exclude = []


