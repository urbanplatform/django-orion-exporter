from django.contrib import admin

from orion_exporter.models import OrionEntity

from orion_exporter.models import OrionServicePath


class OrionServicePathAdminInline(admin.TabularInline):
    model = OrionServicePath
    extra = 0


@admin.register(OrionEntity)
class OrionEntityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_on', 'updated_on']
    inlines = [OrionServicePathAdminInline]


@admin.register(OrionServicePath)
class OrionServicePathAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'entity', 'created_on', 'updated_on']
