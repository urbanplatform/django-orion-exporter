from orion_exporter.api.views import OrionEntitiesAPI
from orion_exporter.api.views import OrionServicePathsAPI
from rest_framework import routers

orion_exporter_router = routers.DefaultRouter()
orion_exporter_router.register(r'entities', OrionEntitiesAPI, base_name='OrionEntities')
orion_exporter_router.register(r'service-paths', OrionServicePathsAPI, base_name='OrionEntities')
