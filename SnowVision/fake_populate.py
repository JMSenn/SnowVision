import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SnowVision.settings')

import django
django.setup()
from django.contrib.auth.models import User
import requests
from SnowVisionApp.models import *
from faker import Faker
import random
import geocoder
from datetime import datetime
from os import walk

# (Site, Project, Context, Sherd, Design, Reference)

fakegen = Faker()
def populate_affiliations():
    fake_affiliations = [
        "Clemson University",
        "University of South Carolina",
        "Furman University",
        "University of Florida",
        "University of Virginia",
    ]

    for aff in fake_affiliations:
        affiliation = Affiliation.objects.create(name = aff)
        affiliation.save()

def populate_profiles(count=20):
    for i in range(count):
        fUsername = fakegen.first_name()
        fEmail = fakegen.email()
        faffiliations = Affiliation.objects.all()
        user = User.objects.create_user(username=fUsername+str(i)+str(random.randint(1,1000)),
                                        email=fEmail,
                                        password="gerundsrfun4%")
        profiles = Profile.objects.all()
        for profile in profiles:
            faffiliation = random.choice(faffiliations)
            profile.affiliation = faffiliation
            profile.save()

def populate_sites(count=20):

    site_dict ={
        'Candy Creek':['Helen', 'Georgia'], #fake,
        'Danville':['Danville','Georgia'],
        'Fairchilds Landing':['Chattahoochee', 'Georgia'],
        'Kolomoki':['Blakely', 'Georgia'],
        'Mandeville': ['Mandeville', 'Louisiana'],
        'Milamo': ['Wheeler County', 'Georgia'],
        'Quartermaster': ['Fort Benning','Georgia'] ,
        'Swift Creek': ['Atlanta', 'Georgia'],
        'Uchee':['Cherokee', 'South Carolina'],
        'Wakulla County': ['Wakulla County','Florida'],
    }

    ecoregion4s = EcoRegionFour.objects.all()

    for site in site_dict:
        site_name = site
        fnumber = fakegen.zipcode()
        ecoregion4 = random.choice(ecoregion4s)

        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'sensor': 'false', 'address': site_dict[site_name][0]+', '+site_dict[site_name][1],'key':"AIzaSyAiIziHoNgvdOUDWJydE1vQVQDCu8DUCAU"}
        r = requests.get(url, params=params)
        results = r.json()['results']
        location = results[0]['geometry']['location']
        flat=location['lat']
        flng=location['lng']


        new_site = Site.objects.get_or_create(
                    name=site_name, number=fnumber,
                    county=site_dict[site_name][0],
                    state =site_dict[site_name][1],
                    eco_region_four=ecoregion4,
                    lat=flat, lng=flng
                      )

        # new_site.save()


def populate_project(count=20):
    '''
    site = models.ManyToManyField(Site)
    excavator = models.CharField(max_length=40)
    start_date = models.DateField()
    name = models.CharField(max_length=100)
    '''

    projects = [
        'Agave Project',
        'Anasazi Heritage Center',
        'Casa Grande Ruins',
        'HovenWeep',
        'Indian Peaks Chapter',
        'Sandals of the Anasazi',
        'Navajo Nation Project',
        'Texas Arrowheads',
        'Southwestern Archaeology',
        'Wester National Parks'
    ]
    for proj in projects:

        fexcavator = fakegen.name()
        fproject_name = proj
        fstart_date = fakegen.past_date(start_date="-30y", tzinfo=None)

        new_project = Project.objects.get_or_create(
            excavator=fexcavator,
            start_date=fstart_date,
            name=fproject_name)

    sites = Site.objects.all()
    projects = Project.objects.all()

    for proj in projects:
        # Generate random number of associated sites between [1,3]
        for i in range(random.randint(1,3)):
            proj.site.add(random.choice(sites))
        proj.save()


def populate_context(count=20):

    sites = Site.objects.all()
    projects = Project.objects.all()
    recov_meths = RecoveryMethod.objects.all()
    screen_types = ScreenType.objects.all()
    curators = Curator.objects.all()

    years = []
    for i in range(1492, 2017):
        years.append(i)


    for i in range(count):
        fproject = random.choice(projects)
        fsite = random.choice(Site.objects.filter(project=fproject))
        frecov_method = random.choice(recov_meths)
        fscreen_type = random.choice(screen_types)
        fname = fakegen.currency_code()
        fcurated_by = random.choice(curators)
        fnorthing = str(fakegen.latitude())
        feasting = str(fakegen.longitude())
        fyear = random.choice(years)

        new_context = Context.objects.get_or_create(
            site=fsite, project=fproject,
            recovery_method=frecov_method, screen_type=fscreen_type,
            name=fname, curator=fcurated_by,
            northing=fnorthing,
            easting=feasting,
            year_excavated=fyear
        )


def populate_reference(count=20):

    journals = Journal.objects.all()

    for i in range(count):
        fjournal = random.choice(journals)
        flast = fakegen.last_name()
        fyear = random.randint(1492, 2017)
        freference = fakegen.words(nb=1)[0]
        fvolume = random.randint(1,500)
        fpage_numbers = str(random.randint(1,3000)) +" - "+ str(random.randint(2,3000))

        new_reference = Reference.objects.get_or_create(
            journal=fjournal, author_last_name=flast,
            year=fyear, title="Lorem Ipsum Title",
            volume=fvolume, page_numbers=fpage_numbers
        )


def populate_design():

    symmetries = Symmetry.objects.all()
    references = Reference.objects.all()
    elements = DesignElement.objects.all()
    greyscale_images = os.listdir("media/greyscale_designs")


    for image_name in greyscale_images:
        os.rename( "media/greyscale_designs/" + image_name, "media/greyscale_designs/" + image_name.replace(" ", ""))
        filename, file_extension = os.path.splitext(image_name)
        #remove white spaces from filename
        filename.replace(" ", "")
        created = False
        # get_or_create returns a tuple where element 1 is a bool indicating creation
        # Query on the design name, if it does not exist, then create with defaults
        while created != True:
            fdesign, created = Design.objects.get_or_create(

            number = filename,
            defaults={'line_filler': True,
                      'completeness': True,
                       'symmetry': random.choice(symmetries)
            })

        fdesign.design_reference.add(random.choice(references))
        fdesign.design_reference.add(random.choice(references))
        fdesign.design_reference.add(random.choice(references))
        fdesign.elements.add(random.choice(elements))
        fdesign.elements.add(random.choice(elements))
        fdesign.elements.add(random.choice(elements))
        fdesign.elements.add(random.choice(elements))
        fdesign.elements.add(random.choice(elements))
        fdesign.symmetry = random.choice(symmetries)
        fdesign.artist = fakegen.name()
        fdesign.framing = fakegen.text(max_nb_chars=32)
        fdesign.line_filler = random.choice([True, False])
        fdesign.completeness = random.choice([True, False])
        fdesign.greyscale_image = "/greyscale_designs/" + image_name
        # curve_image = models.ImageField(blank=True)
        # greyscale_image = models.ImageField(blank=True)

        fdesign.save()


def populate_sherd(count=20):

    profiles = Profile.objects.all()
    contexts = Context.objects.all()
    designs = Design.objects.all()
    imgs = os.listdir("media/sherds")

    for i in range(count):
        fcontext = random.choice(contexts)
        foverstamped = True if i%2==0 else False
        fProfile = random.choice(profiles)
        fsherd_design = random.choice(designs)

        frgb_image = "/sherds/" + imgs.pop()
        new_sherd = Sherd.objects.create(
            context=fcontext,
            overstamped=foverstamped,
            rgb_image=frgb_image,
            profile = fProfile,
            design = fsherd_design,
            )

        new_sherd.save()

def populate_collections():
    profiles = Profile.objects.all()
    for fprofile in profiles:
        collection_1 = Sherd_Collection.objects.create(profile = fprofile, name = "First Collection")
        collection_2 = Sherd_Collection.objects.create(profile = fprofile, name = "Second Collection")
        collection_3 = Sherd_Collection.objects.create(profile = fprofile, name = "Third Collection")

        #adds all profile sherds to a collection
        profile_sherds = Sherd.objects.filter(profile=fprofile)
        for sherd in profile_sherds:
            sherd.collection =random.choice([collection_1,collection_2,collection_3])
            sherd.save()

        collection_1.save()
        collection_2.save()
        collection_3.save()

if __name__ == '__main__':

    print("Deleting previous Database")
    Site.objects.all().delete()
    Project.objects.all().delete()
    Context.objects.all().delete()
    Design.objects.all().delete()
    Sherd.objects.all().delete()
    DesignElement.objects.all().delete()
    Sherd_Collection.objects.all().delete()
    print("Finished deleting")

    print("Populating Affilations...Please Wait")
    populate_affiliations()
    print("Affiliations complete\n")

    print("Populating the Profiles...Please Wait")
    populate_profiles(20)
    print('Profiles Complete\n')

    print("Populating the sites...Please Wait")
    populate_sites()
    print('Sites Complete\n')

    print("Populating the Projects...Please Wait")
    populate_project(20)
    print('Projects Complete\n')

    print("Populating the Contexts...Please Wait")
    populate_context(200)
    print('Contexts Complete\n')

    print("Populating the References...Please Wait")
    populate_reference(100)
    print('References Complete\n')

    designelms = fakegen.words(nb=20)
    for i in designelms:
        DesignElement.objects.get_or_create(name=i)

    print("Populating the Designs...Please Wait")
    populate_design()
    print('Designs Complete\n')

    print("Populating the Sherds...Please Wait")
    populate_sherd(150)
    print('Sherds Complete\n')

    print("Populating the Collections...Please Wait")
    populate_collections()
    print("Collections Complete\n")
