from django.urls import path
from .views import home, city_suggest

urlpatterns = [
    path('', home, name='home'),
    path('suggest/', city_suggest, name='city_suggest'),
]
