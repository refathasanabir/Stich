from django.shortcuts import render, redirect


def measurement_form(request):
    if request.method == "POST":
        # This is where we will capture the POST data and save it to the database later
        return redirect("customers:profiles")
    return render(request, "measurements/form.html")


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from customers.models import MeasurementProfile
from .forms import MeasurementProfileForm


@login_required
def measurement_form_view(request, pk=None):
    profile = None
    if pk:
        profile = get_object_or_404(MeasurementProfile, pk=pk, user=request.user)

    if request.method == "POST":
        form = MeasurementProfileForm(request.POST, instance=profile)
        if form.is_valid():
            measurement = form.save(commit=False)
            measurement.user = request.user
            if measurement.is_default:
                # Unmark other defaults for this user
                MeasurementProfile.objects.filter(user=request.user).update(
                    is_default=False
                )
            measurement.save()
            return redirect("customers:profiles")
    else:
        form = MeasurementProfileForm(instance=profile)

    return render(request, "measurements/form.html", {"form": form, "profile": profile})
