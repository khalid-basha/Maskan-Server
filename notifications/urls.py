from django.urls import path

from notifications.views import create_or_update_token

urlpatterns = [
    path("devices/token/<int:pk>/", create_or_update_token, name="create_or_update_token"),
]
