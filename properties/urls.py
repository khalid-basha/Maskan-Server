from django.urls import path

from properties.views import homes_cards_filtration, home_list, pending_home_list, favourite_home_list, \
    home_images_upload, posted_home_list, home_details, home_not_found, toggle_favorite, visited_home_list, \
    favourite_home_list_api, visited_home_list_api, pending_home_list_api, posted_home_list_api, \
    homes_cards_filtration_api

urlpatterns = [
    path("houses/", homes_cards_filtration, name="houses"),
    path("houses/api/", homes_cards_filtration_api, name="houses"),
    path("home_list/", home_list, name="home_list"),
    path("favourites_home_list/", favourite_home_list, name="favourite_home_list"),
    path("visited_home_list/", visited_home_list, name="visited_home_list"),
    path("pending_home_list/", pending_home_list, name="pending_home_list"),
    path("posted_home_list/", posted_home_list, name="posted_home_list"),
    path("favourites_home_list/api/", favourite_home_list_api, name="favourite_home_list"),
    path("visited_home_list/api/", visited_home_list_api, name="visited_home_list"),
    path("pending_home_list/api/", pending_home_list_api, name="pending_home_list"),
    path("posted_home_list/api/", posted_home_list_api, name="posted_home_list"),
    path("upload/<int:pk>/", home_images_upload, name="upload"),
    path("home/<int:pk>/", home_details, name="home_details"),
    path('home_not_found/', home_not_found, name='home_not_found'),
    path('home/<int:pk>/toggle_favorite/', toggle_favorite, name='toggle_favorite')
]
