# from django.shortcuts import render, redirect


# def measurement_form(request):
#     if request.method == "POST":
#         # This is where we will capture the POST data and save it to the database later
#         return redirect("customers:profiles")
#     return render(request, "measurements/form.html")


# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from customers.models import MeasurementProfile
# from .forms import MeasurementProfileForm


# @login_required
# def measurement_form_view(request, pk=None):
#     profile = None
#     if pk:
#         profile = get_object_or_404(MeasurementProfile, pk=pk, user=request.user)

#     if request.method == "POST":
#         name = request.POST.get("name", "My Profile")
#         relation = request.POST.get("relation", "Self")
#         gender = request.POST.get("gender", "Male")
#         category = request.POST.get("category", "Panjabi")
#         is_default = request.POST.get("is_default") == "on"

#         # Dynamically harvest all measure_* fields into a JSON dictionary
#         values = {}
#         for key, value in request.POST.items():
#             if key.startswith("measure_") and value.strip():
#                 field_name = key.replace("measure_", "").replace("_", " ").title()
#                 values[field_name] = value.strip()

#         if is_default:
#             MeasurementProfile.objects.filter(user=request.user).update(
#                 is_default=False
#             )

#         if profile:
#             profile.name = name
#             profile.relation = relation
#             profile.gender = gender
#             profile.category = category
#             profile.is_default = is_default
#             profile.values = values
#             profile.save()
#         else:
#             MeasurementProfile.objects.create(
#                 user=request.user,
#                 name=name,
#                 relation=relation,
#                 gender=gender,
#                 category=category,
#                 is_default=is_default,
#                 values=values,
#             )

#         messages.success(request, "Measurement profile saved successfully!")
#         return redirect("customers:profiles")

#     return render(request, "measurements/form.html", {"profile": profile})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from customers.models import MeasurementProfile


# @login_required
# def measurement_form_view(request, pk=None):
#     profile = None
#     if pk:
#         profile = get_object_or_404(MeasurementProfile, pk=pk, user=request.user)

#     if request.method == "POST":
#         name = request.POST.get("name", "My Profile")
#         relation = request.POST.get("relation", "Self")
#         gender = request.POST.get("gender", "Male")
#         category = request.POST.get("category", "Panjabi")
#         is_default = request.POST.get("is_default") == "on"

#         # Dynamically harvest all measure_* fields into a JSON dictionary
#         values = {}
#         for key, value in request.POST.items():
#             if key.startswith("measure_") and value.strip():
#                 field_name = key.replace("measure_", "").replace("_", " ").title()
#                 values[field_name] = value.strip()

#         if is_default:
#             MeasurementProfile.objects.filter(user=request.user).update(
#                 is_default=False
#             )

#         if profile:
#             profile.name = name
#             profile.relation = relation
#             profile.gender = gender
#             profile.category = category
#             profile.is_default = is_default
#             profile.values = values
#             profile.save()
#         else:
#             MeasurementProfile.objects.create(
#                 user=request.user,
#                 name=name,
#                 relation=relation,
#                 gender=gender,
#                 category=category,
#                 is_default=is_default,
#                 values=values,
#             )

#         messages.success(request, "Measurement profile saved successfully!")
#         return redirect("customers:profiles")

#     return render(request, "measurements/form.html", {"profile": profile})


@login_required
def measurement_form_view(request, pk=None):
    profile = None
    if pk:
        profile = get_object_or_404(MeasurementProfile, pk=pk, user=request.user)

    if request.method == "POST":
        name = request.POST.get("name", "My Profile")
        relation = request.POST.get("relation", "Self")
        gender = request.POST.get("gender", "Male")
        category = request.POST.get("category", "Panjabi")
        is_default = request.POST.get("is_default") == "on"

        # Keep keys clean without spaces (e.g., 'sleeve_length' instead of 'Sleeve Length')
        values = {}
        for key, value in request.POST.items():
            if key.startswith("measure_") and value.strip():
                field_name = key.replace("measure_", "")
                values[field_name] = value.strip()

        if is_default:
            MeasurementProfile.objects.filter(user=request.user).update(
                is_default=False
            )

        if profile:
            profile.name = name
            profile.relation = relation
            profile.gender = gender
            profile.category = category
            profile.is_default = is_default
            profile.values = values
            profile.save()
        else:
            MeasurementProfile.objects.create(
                user=request.user,
                name=name,
                relation=relation,
                gender=gender,
                category=category,
                is_default=is_default,
                values=values,
            )

        messages.success(request, "Measurement profile saved successfully!")
        return redirect("customers:profiles")

    return render(request, "measurements/form.html", {"profile": profile})


@login_required
def delete_measurement_profile(request, pk):
    """Deletes a specific measurement profile belonging to the user"""
    profile = get_object_or_404(MeasurementProfile, pk=pk, user=request.user)
    profile.delete()
    messages.success(request, "Measurement profile deleted successfully!")
    return redirect("customers:profiles")
