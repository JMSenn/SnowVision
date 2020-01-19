import os
import logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SnowVision.settings')

import django
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from time import sleep
from SnowVisionApp import models

django.setup()
logger = logging.getLogger('__name__')


# Passes the work to the matching algoritm
def does_match(img=None, dimensional=None):
    return models.Design.objects.filter(symmetry__name__iexact="asymmetrical")[:5]


def match(sherd_pk ,current_site):
    success = True;
    logger.error('Entered blackbox.py')
    sherd = models.Sherd.objects.get(pk=sherd_pk)
    # Simulates processing time, remove when algoritm is implemented
    sleep(2)
    # Pass Sherd RGB and Dimensional data here
    designs = does_match()
    print(designs)

    # Create a match object for each match. Maybe set a minimum match threshold?
    for design in designs:
        match_pct = models.MatchPercentage.objects.create(
            design=design, sherd=sherd, percent=.5)

        match_pct.save()

    logger.warning("Exiting blackbox.py")

    # Generate and send email to user notifying them that the analysis is complete
    message = render_to_string('SnowVisionApp/sherd_analysis_complete.html',
        {
            'user': sherd.profile.user,
            'domain': current_site,
            'pk': sherd.pk
        })
    subject = "Sherd Analysis Complete"
    to_email = sherd.profile.user.email
    email = EmailMessage(subject, message, to=[to_email])

    # Remove line below in production
    email.send()

    return email
