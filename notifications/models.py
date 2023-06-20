import requests
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import Signal, receiver
from properties.models import Home

url = 'https://exp.host/--/api/v2/push/send'


# Create your models here.
class UserDevicesToken(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    token = models.CharField(max_length=50)


# Signal triggered when a home is favorite
home_favourite = Signal()

# Signal triggered when a schedule is reserved
reserve_schedule = Signal()


@receiver(pre_save, sender=Home)
def handle_home_updated(sender, instance, **kwargs):
    try:
        owner = instance.owner
        token = UserDevicesToken.objects.get(pk=owner.id)
        headers = {'Content-Type': 'application/json'}
        data = {
            "to": f"{token.token}",
            "sound": "default",
            "title": "Maskan",
            "body": "Maskan just approved your property!",
            "_displayInForeground": True,
            "priority": "high"
        }
        if instance.pk is not None:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.is_pending != instance.is_pending:
                if not instance.is_pending:
                    response = requests.post(url, json=data, headers=headers)
                    # Check the response status
                    if response.status_code == 200:
                        print("Post Notification sent successfully!")
                    else:
                        print("Failed to send notification:", response.text)
                else:
                    print("Failed to send notification")
    except UserDevicesToken.DoesNotExist:
        print("User does not exist")


@receiver(home_favourite)
def handle_home_favourite(sender, **kwargs):
    try:
        owner_id = kwargs.get('owner_id')
        token = UserDevicesToken.objects.get(pk=owner_id.id)
        user = kwargs.get('user')
        headers = {'Content-Type': 'application/json'}
        data = {
            "to": f"{token.token}",
            "sound": "default",
            "title": "Maskan",
            "body": f"{user.username.title()} Liked Your Property!",
            "_displayInForeground": True,
            "priority": "high"
        }

        response = requests.post(url, json=data, headers=headers)
        # Check the response status
        if response.status_code == 200:
            print("Favorite Notification sent successfully!")
        else:
            print("Failed to send notification:", response.text)
    except UserDevicesToken.DoesNotExist:
        print("User does not exist")


@receiver(reserve_schedule)
def handle_reserve_schedule(sender, **kwargs):
    try:
        owner_id = kwargs.get('owner_id')
        token = UserDevicesToken.objects.get(pk=owner_id.id)
        headers = {'Content-Type': 'application/json'}
        data = {
            "to": f"{token.token}",
            "sound": "default",
            "title": "Maskan",
            "body": f"Your property just got a new reservation!",
            "_displayInForeground": True,
            "priority": "high"
        }

        response = requests.post(url, json=data, headers=headers)
        # Check the response status
        if response.status_code == 200:
            print("reserve Notification sent successfully!")
        else:
            print("Failed to send notification:", response.text)
    except UserDevicesToken.DoesNotExist:
        print("User does not exist")