from orion_exporter.api.filters import OrionEntityFilter
from orion_exporter.api.filters import OrionServicePathFilter
from orion_exporter.api.serializers import OrionEntitySerializer
from orion_exporter.api.serializers import OrionServicePathSerializer
from orion_exporter.models import OrionEntity
from orion_exporter.models import OrionServicePath
from rest_framework import viewsets
from rest_framework.filters import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter


class OrionEntitiesAPI(viewsets.ReadOnlyModelViewSet):
    """ API endpoint for orion entities management. """

    authentication_classes = []
    permission_classes = []

    queryset = OrionEntity.objects.all().order_by('-created_on')
    serializer_class = OrionEntitySerializer
    filter_class = OrionEntityFilter
    token = None
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ('id', 'name', )
    ordering_fields = '__all__'


class OrionServicePathsAPI(viewsets.ReadOnlyModelViewSet):
    """ API endpoint for orion services paths management. """

    authentication_classes = []
    permission_classes = []

    queryset = OrionServicePath.objects.all().order_by('-created_on')
    serializer_class = OrionServicePathSerializer
    filter_class = OrionServicePathFilter
    token = None
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    search_fields = ('id', 'name', )
    ordering_fields = '__all__'
