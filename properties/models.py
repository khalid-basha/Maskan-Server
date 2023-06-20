from datetime import datetime, date
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.gis.db import models as geo_models
from django.utils.safestring import mark_safe
from storages.backends.s3boto3 import S3Boto3Storage

# Create your models here.
HOME_TYPES_OPTIONS = (
    ('AP', 'APARTMENT'),
    ('HO', 'HOUSE'),
)
STATE_TYPES_OPTIONS = (
    ('R', 'RENT'),
    ('S', 'SELL'),
)


def current_year():
    return date.today().year


def upload_to_properties(instance, filename):
    return f"properties/{instance.home.owner.id}/{instance.home.id}/images/{filename}"


def upload_to_ownership_record(instance, filename):
    return f"properties/{instance.home.owner.id}/{instance.home.id}/ownership_record/{filename}"


class Home(models.Model):
    price = models.PositiveIntegerField(verbose_name='Price')
    area = models.PositiveIntegerField(help_text='The Area of the house in square foot', default=0)
    owner = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name="properties")
    favourite_by = models.ManyToManyField(to=get_user_model(), related_name='favourites',
                                          related_query_name='favourite_by')
    visited_by = models.ManyToManyField(to=get_user_model(), related_name='visited',
                                        related_query_name='visited_by')
    description = models.TextField(blank=True)
    add_date = models.DateTimeField(editable=False)
    built_year = models.PositiveSmallIntegerField(help_text='The year when the home built, limits[1900,current year]',
                                                  validators=[MaxValueValidator(current_year()),
                                                              MinValueValidator(1900)])
    views = models.PositiveIntegerField(help_text='How many times do the users saw this home', default=0)
    type = models.CharField(choices=HOME_TYPES_OPTIONS, max_length=3)
    state = models.CharField(choices=STATE_TYPES_OPTIONS, max_length=2)
    is_pending = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.add_date = datetime.now()
        return super(Home, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class House(models.Model):
    home = models.OneToOneField('Home', on_delete=models.CASCADE)
    number_of_floors = models.PositiveSmallIntegerField(verbose_name='Number of floors')
    land_area = models.PositiveSmallIntegerField(help_text='the area of the land a house was built on')


class Apartment(models.Model):
    home = models.OneToOneField('Home', on_delete=models.CASCADE)
    floor = models.PositiveSmallIntegerField(help_text='the floor where the apartment is in the building')
    out_of_floors = models.PositiveSmallIntegerField(help_text='number of floors in the building')


class Location(models.Model):
    home = models.OneToOneField('Home', on_delete=models.CASCADE, related_name='location')
    coordinates = geo_models.PointField()
    address = models.CharField(max_length=190)
    city = models.CharField(max_length=50)


class LivingSpace(models.Model):  # need a signal
    home = models.OneToOneField('Home', on_delete=models.CASCADE, related_name='living_space')
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    kitchens = models.PositiveSmallIntegerField(default=0)
    balconies = models.PositiveSmallIntegerField(default=0)
    halls = models.PositiveSmallIntegerField(default=0)
    living_rooms = models.PositiveSmallIntegerField(default=0)


class Ownership(models.Model):
    home = models.OneToOneField('Home', on_delete=models.CASCADE, related_name='ownership')
    record = models.ImageField(upload_to=upload_to_ownership_record, storage=S3Boto3Storage())
    is_accepted = models.BooleanField(default=False)
    is_viewable = models.BooleanField(default=False)

    def record_preview(self):  # new
        return mark_safe(f'<img src = "{self.record.url}" width = "300"/>')


class Features(models.Model):
    data = models.JSONField()
    home = models.OneToOneField('Home', on_delete=models.CASCADE, related_name='features')

    def __str__(self):
        return str(self.id)

    def features(self):
        representation = "<ul>"
        if self.data:
            for e in self.data:
                representation = representation + f'<li>{str(e["key"]).title()}</li>'
        representation = representation + "</ul>"
        return mark_safe(representation)


class Image(models.Model):
    home = models.ForeignKey('Home', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=upload_to_properties, storage=S3Boto3Storage())

    def image_preview(self):  # new
        return mark_safe(f'<img src = "{self.image.url}" width = "300"/>')

    def __str__(self):
        return 'Image {}'.format(self.id)
