from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url="/login/")
def dashboard(request):
    return render(request, "riders/dashboard.html")


# @login_required(login_url="/login/")
# def verify_delivery_view(request, order_id):
#     order = get_object_or_404(Order, order_id=order_id)

#     if request.method == "POST":
#         entered_pin = request.POST.get("delivery_pin", "").strip()

#         if order.delivery_pin and order.delivery_pin == entered_pin:
#             order.status = "Delivered"
#             order.save()
#             messages.success(request, "Delivery successfully verified with PIN!")
#             return redirect("riders:dashboard")
#         else:
#             messages.error(
#                 request, "Incorrect security PIN. Please check with the customer."
#             )

#     return render(request, "riders/verify_delivery.html", {"order": order})
