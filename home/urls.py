from django.urls import path
from .views import *

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
    path('xml/', home_xml, name='home_xml'),
    path('feeders/', feeders, name='feeders'),
    path('feeders/<feeder_id>/', feeder, name='feeder'),
    path('items/', items, name='items'),
    path('items/<item_id>/', item, name='item'),
    path('users/', users, name='users'),
    path('users/<user_id>/', user, name='user'),
    path('info/', info, name='info'),
]
