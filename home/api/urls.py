from django.urls import path
from .views import *

urlpatterns = [
    path('retrieve/', ListFeeders.as_view()),
    path('create/', CreateFeeder.as_view()),
]
