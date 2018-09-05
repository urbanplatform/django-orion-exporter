from django_filters.rest_framework import FilterSet

from orion_exporter.models import OrionEntity

from orion_exporter.models import OrionServicePath


class OrionEntityFilter(FilterSet):
    class Meta:
        model = OrionEntity
        fields = {
            'id': ['exact'],
            'name': ['exact'],
            'created_on': ['lte', 'gte'],
            'updated_on': ['lte', 'gte'],
        }


class OrionServicePathFilter(FilterSet):
    class Meta:
        model = OrionServicePath
        fields = {
            'id': ['exact'],
            'entity': ['exact'],
            'name': ['exact'],
            'created_on': ['lte', 'gte'],
            'updated_on': ['lte', 'gte'],
        }
