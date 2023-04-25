from django.contrib import admin
from django.urls import path, include

from UI.views import main_page, calculate, saved

urlpatterns = [
    path("", main_page, name="main_page"),
    path("saved/", saved, name="saved"),
    path("calculate/", calculate, name="calculate")
]