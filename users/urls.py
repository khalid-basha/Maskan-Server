from django.urls import path

from users.views import activate, user_list, profile_details, user_login, logout_view, account, user_from_token


urlpatterns = [
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('users/', user_list, name='user_list'),
    path('users/<str:token>/', user_from_token, name='user_from_token'),
    path('account/<int:pk>/', account, name='account'),
    path('profile/<int:pk>/', profile_details, name='user_detail'),
    path('login/', user_login, name='login'),
    path('logout/', logout_view, name='logout'),
    # path('add_users', add_users_view),
]
