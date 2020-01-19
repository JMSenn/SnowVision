import datetime, requests

from django.core import validators
from django.core.exceptions import ValidationError
from django.urls import reverse

from django.db import models
from django.db.models.signals import post_save

from django.dispatch import receiver
from django.contrib.auth.models import User

# extends django user class
# enables the profile to be associated with collections,sherds, and affiliations
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    affiliation = models.ForeignKey('Affiliation', null=True, blank=True, on_delete=models.SET_NULL)
   
    @receiver(post_save, sender=User)
    def update_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()

    def __str__(self):
        return self.user.username


#
class Affiliation(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)

    def __str__(self):
        return self.name


# represents a real world location where sherds have or may be founds
class Site(models.Model):
    number = models.CharField(max_length=32 , primary_key=True)
    eco_region_four = models.ForeignKey('EcoRegionFour', on_delete=models.PROTECT)
    name = models.CharField(max_length=32)
    state = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    # fields to be left empty until valid creation then filled by model_created_or_updated below
    lat = models.DecimalField(max_digits=8, decimal_places=3,blank=True)
    lng = models.DecimalField(max_digits=8, decimal_places=3,blank=True)

    # overwritten save function calls get_location to set latitude and longitude

    def get_location(self, location):
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = {'sensor': 'false', 'address': location,'key':""}
        r = requests.get(url, params=params)
        if(r.json()["status"]=="OK"):
            results = r.json()['results']
            return results

        else:
            raise ValidationError("Invalid Location")

    def save(self, *args, **kwargs):
        location_string = self.county +", "+self.state
        results = self.get_location(location_string)

        location = results[0]['geometry']['location']
        self.lat = location['lat']
        self.lng = location['lng']
        super(Site,self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# nationally recognized type of categorizing regions
class EcoRegionThree(models.Model):
    region_type = models.CharField(max_length=200)

    def __str__(self):
        return self.region_type


# nationally recognized method of categorizing regions
# each eco region four is a subcategory of eco region three
class EcoRegionFour(models.Model):
    eco_region_three = models.ForeignKey(EcoRegionThree, on_delete=models.PROTECT)
    region_type = models.CharField(max_length=200)

    def __str__(self):
        return self.region_type


# a project is an archaeological undertaking that may be affiliated with one or more sites
class Project(models.Model):
    site = models.ManyToManyField(Site)
    name = models.CharField(max_length=100)
    excavator = models.CharField(max_length=40)
    start_date = models.DateField()

    def __str__(self):
        return (self.name)


# a context is a subcategory of a give site and project
# this contains more specific information about the discovery method of a sherd
class Context(models.Model):
    site = models.ForeignKey(Site, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    recovery_method = models.ForeignKey('RecoveryMethod', null=True, on_delete=models.SET_NULL)
    screen_type = models.ForeignKey('ScreenType', null=True, on_delete=models.SET_NULL)
    curator = models.ForeignKey('Curator', null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=32, null=True)
    northing = models.CharField(max_length=32, null=True)
    easting = models.CharField(max_length=32, null=True)

    # contained to associate with profile since users can create contexts
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
    YEAR_CHOICES = [(i,i) for i in range(1492, 2017)]
    year_excavated = models.IntegerField(
        ('year'), choices=YEAR_CHOICES, default=datetime.datetime.now().year)

    def get_absolute_url(self):
        return reverse("SnowVisionApp:uploadSherd")

    def __str__(self):
        return self.name

    def full_str(self):
        full_string= self.name+","+self.recovery_method.name+","+"Screen:"+self.screen_type.name+self.northing
        full_string +=self.northing+","+self.curator.name
        return full_string


class Curator(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# contains information about screen that may or may not have been used to get sherd in a context
class ScreenType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# method by which artifacts in context was discovered
class RecoveryMethod(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name

# main database item to be collected
# contains images and three dimensional data of sherds to be submitted by users
class Sherd(models.Model):
    # profile affiliated since users can create sherds
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)

    # main upward affilation
    context = models.ForeignKey(Context, on_delete=models.PROTECT)
    overstamped = models.BooleanField(blank=True)

    # main downward affiliaton
    design = models.ForeignKey('Design', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rgb_image = models.ImageField(
        upload_to='sherds')
    dimensional_data = models.FileField(blank=True,upload_to ="dimensional_data")
    private = models.BooleanField(default = False)
    collection = models.ForeignKey("Sherd_Collection", blank=True, null=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("user_profile")

    def __str__(self):
        context_str = getattr(self.context, "__str__")
        return str(self.context.site.name + " " + self.context.project.name + " " + context_str())


class Sherd_Collection(models.Model):
    name = models.CharField(max_length = 200)
    profile = models.ForeignKey('Profile', on_delete=models.DO_NOTHING)
    private = models.BooleanField(default = False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("user_profile")


# intermediate class to associate algorithm matches to a design
# with a particulate sherd
# created in system. Not by admin or users
class MatchPercentage(models.Model):
    design = models.ForeignKey('Design', on_delete=models.DO_NOTHING)
    sherd = models.ForeignKey('Sherd', on_delete=models.DO_NOTHING)
    percent = models.FloatField()


# found on sherds
class Design(models.Model):
    # universal identifier of design
    # has some information in number that may trace back origin of design
    number = models.CharField(max_length=32, primary_key=True)

    # design will have a reference to external source
    design_reference = models.ManyToManyField('Reference')

    # elements found in a particular design
    elements = models.ManyToManyField('DesignElement')
    symmetry = models.ForeignKey('Symmetry', on_delete=models.DO_NOTHING)

    line_filler = models.BooleanField()

    # is the design complete or partial
    completeness = models.BooleanField()
    framing = models.CharField(max_length=32, blank=True)
    artist = models.CharField(max_length=100)
    # images to be used in algorithmic evaulation of sherd
    curve_image = models.ImageField(blank=True, upload_to='curve_images')

    # black and white image associated with design
    # pulled for user reference
    greyscale_image = models.ImageField(blank=True, upload_to='greyscale_image')

    def __str__(self):
        return self.number


# types of symmetry that a sherd can have
class Symmetry(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


# elements found within a design
class DesignElement(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name


# journals that publish sherd related material
class Journal(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# citation of source
class Reference(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.DO_NOTHING)
    author_last_name = models.CharField(max_length=30)
    year = models.CharField(max_length=4)
    title = models.CharField(max_length=50)
    volume =  models.CharField(max_length=20)
    page_numbers = models.CharField(max_length=20)

    def __str__(self):
        return self.title
