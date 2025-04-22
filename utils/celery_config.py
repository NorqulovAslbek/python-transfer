# from celery import Celery
#
# app = Celery(
#     'utils',
#     broker='redis://redis:6379/0',  # Redis in Docker
#     backend='redis://redis:6379/0',
#     include=['utils.tasks']
# )
#
# # Configure Celery to use Django settings
# app.conf.update(
#     task_serializer='json',
#     accept_content=['json'],
#     result_serializer='json',
#     timezone='UTC',
#     enable_utc=True,
# )
#
# # Load Django settings
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# # Auto-discover tasks in Django apps
# app.autodiscover_tasks()
#
# # Configure Celery Beat schedule
# app.conf.beat_schedule = {
#     'send-hourly-report': {
#         'task': 'utils.tasks.send_telegram_report',
#         'schedule': 60.0,  # Every hour
#     },
#     'send-daily-report': {
#         'task': 'utils.tasks.send_telegram_report',
#         'schedule': 86400.0,  # Every day
#     },
# }
