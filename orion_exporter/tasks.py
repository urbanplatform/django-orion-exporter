from celery import task
from django.core.management import call_command


@task(queue='orion_queue', name='send_to_orion')
def send_to_orion_task():
    call_command('send_to_orion')
