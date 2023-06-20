from django.urls import path

from reservations.views import time_slots_list_short, reserve_time_slot, time_slot_list

urlpatterns = [
    path("slots/", time_slot_list, name="create_time_slot"),
    path("short_slots/", time_slots_list_short, name="time_slots_list_short"),
    path("reserve/<int:pk>/", reserve_time_slot, name="reserve_time_slot"),
]
