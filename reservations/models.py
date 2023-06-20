from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from properties.models import Home


# Create your models here.
class TimeSlot(models.Model):
    start_time = models.PositiveSmallIntegerField()
    end_time = models.PositiveSmallIntegerField()
    date = models.DateField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='time_slots')
    home = models.ForeignKey(Home, on_delete=models.CASCADE, related_name='reservations', null=True, blank=True)
    reserved_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='reservations', blank=True,
                                    null=True)


@receiver(post_save, sender=TimeSlot)
@receiver(post_delete, sender=TimeSlot)
def delete_expired_time_slots(sender, **kwargs):
    # Get the current date
    today = date.today()
    yesterday = today - timedelta(days=1)
    TimeSlot.objects.filter(date__lte=yesterday, reserved_by__isnull=True).delete()
