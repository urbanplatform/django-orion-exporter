# from __future__ import print_function
#
# import gevent
# from gevent import monkey
#
# monkey.patch_all(thread=False)

from django.core.management.base import BaseCommand

from orion_exporter.models import OrionEntity


class Command(BaseCommand):
    """
    Send to Orion Context Broker all the objects from models
    inherited from OrionEntity
    """

    @staticmethod
    def send_request(obj):
        obj.send_to_orion(obj)

    def parse_models(self, models):
        # tasks = []
        for model in models:
            if model._meta.abstract:  # If model is abstract
                self.parse_models(model.__subclasses__())
            else:  # If model is not abstract
                objects = model.objects.filter(sent_to_orion=False)
                for obj in objects:
                    self.send_request(obj)
                    # tasks.append(gevent.spawn(self.send_request, obj))

        # gevent.wait(tasks)

    def handle(self, *args, **options):
        # Get inherited model from Orion exporter model and get their objects
        self.parse_models(OrionEntity.__subclasses__())
