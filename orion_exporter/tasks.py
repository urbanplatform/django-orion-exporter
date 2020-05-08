from __future__ import absolute_import, unicode_literals
from gevent import monkey
monkey.patch_all(thread=False)

from celery import task
from orion_exporter.models import OrionEntity
from django.conf import settings

import gevent
from gevent import pool


def send_request(obj):
    obj.send_to_orion(obj.__class__.__name__, str(obj.id), None, None, None, None)


@task(queue='orion_queue', name='send_to_orion')
def send_to_orion_task():
    pool_size = getattr(settings, 'REQUESTS_POOL_SIZE', 1)
    p = pool.Pool(pool_size)
    tasks = []
    for subclass in OrionEntity.__subclasses__():
        to_send = subclass.objects.filter(sent=False)
        for obj in to_send:
            tasks.append(p.spawn(send_request, obj))
    gevent.joinall(tasks)