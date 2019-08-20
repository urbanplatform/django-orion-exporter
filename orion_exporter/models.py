from django.db import models


class OrionEntity(models.Model):
    name = models.CharField(
        'Entity Name', unique=True, max_length=255, null=False, blank=False
    )
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name='created on'
    )
    updated_on = models.DateTimeField(
        auto_now=True, verbose_name='updated on'
    )

    def __str__(self):
        return "Entity {}".format(self.name)

    class Meta:
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'


class OrionServicePath(models.Model):
    entity = models.ForeignKey(
        OrionEntity, null=False, blank=False, verbose_name='Entity', related_name='entity', on_delete=models.CASCADE
    )
    name = models.CharField(
        'Service Path', max_length=255, null=False, blank=False
    )
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name='created on'
    )
    updated_on = models.DateTimeField(
        auto_now=True, verbose_name='updated on'
    )

    def __str__(self):
        return "Entity {}".format(self.name)

    class Meta:
        verbose_name = 'Service Path'
        verbose_name_plural = 'Service Paths'
