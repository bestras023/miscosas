from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('login/', log_in, name='log_in'),
    path('log_out/', log_out, name='log_out'),
]