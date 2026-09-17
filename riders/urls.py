from django.urls import path
from django.http import HttpResponse

app_name = "riders"


from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url="/login/")
def dashboard(request):
    return render(request, "riders/dashboard.html")


urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
]
