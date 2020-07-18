from django.urls import path
from .views import *

urlpatterns = [
    path('retrieve/', ListUsers.as_view()),
    path('register/', RegisterUser.as_view()),
    path('login/', LoginUser.as_view()),
]
