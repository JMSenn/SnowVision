from __future__ import absolute_import, unicode_literals
import logging

from django.core.mail import EmailMessage

from celery import shared_task
from SnowVisionApp import blackbox

logger = logging.getLogger(__name__)

@shared_task
def match_to_design(sherd, current_site):
    logger.warning("Received in tasks.match_to_design")
    message = blackbox.match(sherd, current_site)
    email.send()
    return
