# transfer/tasks.py
from celery import shared_task

@shared_task(name='transfer.celery.task.asl_yiban')
def asl_yiban():
    return True