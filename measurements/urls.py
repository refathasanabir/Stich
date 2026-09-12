from django.urls import path
from . import views

app_name = "measurements"

urlpatterns = [
    path("new/", views.measurement_form, name="new_measurement"),
    path("new/", views.measurement_form, name="new"),
    path("add/", views.measurement_form_view, name="add_measurement"),
    path("edit/<int:pk>/", views.measurement_form_view, name="edit_measurement"),
]
