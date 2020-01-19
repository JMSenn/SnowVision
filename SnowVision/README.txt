This the Snow Vision project READ ME file.
Please read this entire file before running any scripts
or making an changes to the file

INSTALLED PACKAGES:
amqp==2.2.1
billiard==3.5.0.3
celery==4.0.2
certifi==2017.4.17
chardet==3.0.4
click==6.7
decorator==4.0.11
Django==1.11.3
django-betterforms==1.1.4
django-celery-results==1.0.1
django-lockdown==1.4.2
et-xmlfile==1.0.1
Faker==0.7.17
geocoder==1.23.1
idna==2.5
jdcal==1.3
kombu==4.0.2
olefile==0.44
openpyxl==2.4.8
Pillow==4.1.1
psycopg2==2.7.1
python-dateutil==2.6.0
python-magic==0.4.13
pytz==2017.2
ratelim==0.1.6
requests==2.18.1
six==1.10.0
urllib3==1.21.1
vine==1.1.4
xlrd==1.0.0
xlwt==1.2.0


SCRIPTS:
initial_populate.py : This is a script that should be run if the database
is dropped. This will not populate user submitted values. This script DOES
populate values that should always be in the database
(symmetry types, eco regions, etc.)

fake_populate.py : Populates the database with fake data for testing.
Some aspects of the fake data are real, but most values are fake.
Running this will delete all previous entries in the database except
those filled in initial_populate.py

MEDIA FILES:
