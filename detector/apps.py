from django.apps import AppConfig


class DetectorConfig(AppConfig):
    name = 'detector'
    # def ready(self):
    #     from vibe_detector.celery_app import app as celery_app