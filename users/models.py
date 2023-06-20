from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from phonenumber_field.modelfields import PhoneNumberField
from users.managers import UserManager


# Create your models here.
class User(AbstractUser):
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    objects = UserManager()
    REQUIRED_FIELDS = ['email', 'date_of_birth', 'phone_number']

    def __str__(self):
        return self.username


def upload_to_profile(instance, filename):
    return f"users/{instance.user.username}/profile_pictures/{filename}"


def upload_to_id(instance, filename):
    return f"users/{instance.user.username}/ID_card/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to=upload_to_profile, null=True)
    ID_card = models.ImageField(upload_to=upload_to_id, null=True)

    def __str__(self):
        return self.user.username

    def profile_picture_preview(self):  # new
        return mark_safe(f'<img src = "{self.profile_picture.url}" width = "300"/>')

    def ID_card_preview(self):  # new
        return mark_safe(f'<img src = "{self.ID_card.url}" width = "300"/>')


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
