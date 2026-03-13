from __future__ import absolute_import, unicode_literals

import os
import sys
from celery import Celery
from dotenv import load_dotenv

import django

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vibe_detector.settings")


django.setup()

app = Celery("vibe_detector")

app.config_from_object("django.conf:settings", namespace="CELERY")


app.autodiscover_tasks()

app.conf.update(
    task_always_eager=False,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    worker_prefetch_multiplier=1,
    worker_concurrency=1,
    broker_connection_retry_on_startup=True,
)


import detector.scan_repo_tasks
import detector.scan_website_tasks
import detector.verify_email_tasks