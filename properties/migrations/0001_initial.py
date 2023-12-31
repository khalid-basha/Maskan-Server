# Generated by Django 4.1.7 on 2023-05-03 15:04

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import properties.models
import storages.backends.s3boto3


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Home',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(verbose_name='Price')),
                ('area', models.PositiveIntegerField(default=0, help_text='The Area of the house in square feet')),
                ('description', models.TextField(blank=True)),
                ('add_date', models.DateTimeField(editable=False)),
                ('built_year', models.PositiveSmallIntegerField(help_text='The year when the home built, limits[1900,current year]', validators=[django.core.validators.MaxValueValidator(2023), django.core.validators.MinValueValidator(1900)])),
                ('views', models.PositiveIntegerField(default=0, help_text='How many times do the users saw this home')),
                ('type', models.CharField(choices=[('AP', 'APARTMENT'), ('HO', 'HOUSE')], max_length=3)),
                ('state', models.CharField(choices=[('R', 'RENT'), ('S', 'SELL')], max_length=2)),
                ('is_pending', models.BooleanField(default=True)),
                ('favourite_by', models.ManyToManyField(related_name='favourites', related_query_name='favourite_by', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties', to=settings.AUTH_USER_MODEL)),
                ('visited_by', models.ManyToManyField(related_name='visited', related_query_name='visited_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ownership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record', models.ImageField(storage=storages.backends.s3boto3.S3Boto3Storage(), upload_to=properties.models.upload_to_ownership_record)),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_viewable', models.BooleanField(default=False)),
                ('home', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ownership', to='properties.home')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('address', models.CharField(max_length=190)),
                ('city', models.CharField(max_length=50)),
                ('home', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='location', to='properties.home')),
            ],
        ),
        migrations.CreateModel(
            name='LivingSpace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bedrooms', models.PositiveSmallIntegerField(default=0)),
                ('bathrooms', models.PositiveSmallIntegerField(default=0)),
                ('kitchens', models.PositiveSmallIntegerField(default=0)),
                ('balconies', models.PositiveSmallIntegerField(default=0)),
                ('halls', models.PositiveSmallIntegerField(default=0)),
                ('living_rooms', models.PositiveSmallIntegerField(default=0)),
                ('home', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='living_space', to='properties.home')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(storage=storages.backends.s3boto3.S3Boto3Storage(), upload_to=properties.models.upload_to_properties)),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='properties.home')),
            ],
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_floors', models.PositiveSmallIntegerField(verbose_name='Number of floors')),
                ('land_area', models.PositiveSmallIntegerField(help_text='the area of the land a house was built on')),
                ('home', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='properties.home')),
            ],
        ),
        migrations.CreateModel(
            name='Features',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.JSONField()),
                ('home', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='properties.home')),
            ],
        ),
        migrations.CreateModel(
            name='Apartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('floor', models.PositiveSmallIntegerField(help_text='the floor where the apartment is in the building')),
                ('out_of_floors', models.PositiveSmallIntegerField(help_text='number of floors in the building')),
                ('home', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='properties.home')),
            ],
        ),
    ]
