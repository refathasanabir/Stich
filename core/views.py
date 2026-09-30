from pathlib import Path

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q

from .models import Design, UserProfile
from tailors.models import TailorShop
from adminpanel.models import Approval

# =========================================================
# PUBLIC PAGES
# =========================================================


def home(request):
    return render(request, "core/home.html")


def gallery(request):
    return gallery_view(request)


def pricing(request):
    return render(request, "core/pricing.html")


def contact(request):
    return render(request, "core/contact.html")


# =========================================================
# USER ROLE REDIRECTION
# =========================================================


def redirect_based_on_role(user):
    """
    Redirect authenticated users according to their database role.
    Admin privileges come from Django's staff/superuser flags.
    """

    if user.is_staff or user.is_superuser:
        return redirect("adminpanel:dashboard")

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        messages.warning(None, "Your account profile is missing.") if False else None
        return redirect("core:home")

    if profile.role == "Customer":
        return redirect("customers:dashboard")

    if profile.role == "Tailor":
        return redirect("tailors:dashboard")

    if profile.role == "Rider":
        return redirect("riders:dashboard")

    return redirect("core:home")


# =========================================================
# LOGIN
# =========================================================


def login_view(request):

    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)

    selected_role = request.POST.get("role", "Customer")
    identifier = ""

    if request.method == "POST":

        identifier = request.POST.get("identifier", "").strip()

        password = request.POST.get("password", "")

        allowed_roles = {
            "Customer",
            "Tailor",
            "Rider",
            "Admin",
        }

        if selected_role not in allowed_roles:

            messages.error(request, "Please select a valid account type.")

        elif not identifier or not password:

            messages.error(request, "Enter your email or username and password.")

        else:

            # ---------------------------------------------
            # Allow login using username or email address.
            # ---------------------------------------------

            username = identifier

            if "@" in identifier:

                matching_users = User.objects.filter(email__iexact=identifier)

                if matching_users.count() == 1:
                    username = matching_users.first().username

            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user is None:

                messages.error(
                    request,
                    "Incorrect credentials, or your account "
                    "has not yet been activated.",
                )

            else:

                # -----------------------------------------
                # Read actual role from the database.
                # -----------------------------------------

                if user.is_staff or user.is_superuser:

                    actual_role = "Admin"

                else:

                    try:
                        actual_role = user.profile.role

                    except UserProfile.DoesNotExist:
                        actual_role = None

                # -----------------------------------------
                # Validate selected role.
                # -----------------------------------------

                if actual_role is None:

                    messages.error(
                        request,
                        "Your user profile is missing. "
                        "Please contact an administrator.",
                    )

                elif actual_role != selected_role:

                    messages.error(
                        request,
                        "This account does not match " "the selected login role.",
                    )

                else:

                    login(request, user)

                    return redirect_based_on_role(user)

    return render(
        request,
        "core/login.html",
        {
            "selected_role": selected_role,
            "identifier": identifier,
        },
    )


# =========================================================
# REGISTRATION DOCUMENT VALIDATION
# =========================================================

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

MAX_DOCUMENT_SIZE = 5 * 1024 * 1024


def validate_registration_document(document):
    """
    Basic extension and size validation.
    Stronger file verification and private document
    storage are required before production deployment.
    """

    if not document:

        raise ValidationError("Please upload the required document.")

    extension = Path(document.name).suffix.lower()

    if extension not in ALLOWED_DOCUMENT_EXTENSIONS:

        raise ValidationError("Only PDF, JPG, JPEG and PNG files are accepted.")

    if document.size > MAX_DOCUMENT_SIZE:

        raise ValidationError("The maximum document size is 5 MB.")


# =========================================================
# REGISTER
# =========================================================


def register_view(request):

    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)

    selected_role = request.POST.get(
        "role",
        "Customer",
    )

    if request.method == "POST":

        role = selected_role

        # ---------------------------------------------
        # Common registration fields
        # ---------------------------------------------

        full_name = request.POST.get("full_name", "").strip()

        

        email = request.POST.get("email", "").strip()

        username = email

        phone = request.POST.get("phone", "").strip()

        password = request.POST.get("password", "")

        confirm_password = request.POST.get("confirm_password", "")

        # ---------------------------------------------
        # Role-specific registration fields
        # ---------------------------------------------

        shop_name = request.POST.get("shop_name", "").strip()

        vehicle_type = request.POST.get("vehicle_type", "").strip()

        trade_license = request.FILES.get("trade_license")

        driving_license = request.FILES.get("driving_license")

        errors = []

        # ---------------------------------------------
        # Role validation
        # ---------------------------------------------

        if role not in {
            "Customer",
            "Tailor",
            "Rider",
        }:

            errors.append("Please select a valid registration role.")

        # ---------------------------------------------
        # Required field validation
        # ---------------------------------------------

        if not all(
            [
                full_name,
                username,
                email,
                phone,
                password,
                confirm_password,
            ]
        ):

            errors.append("Please complete all required fields.")

        # ---------------------------------------------
        # Password validation
        # ---------------------------------------------

        if password != confirm_password:

            errors.append("Passwords do not match.")

        # elif password:

        #     try:

        #         validate_password(password)

        #     except ValidationError as exc:

        #         errors.extend(exc.messages)

        # ---------------------------------------------
        # Email validation
        # ---------------------------------------------

        if email:

            try:

                validate_email(email)

            except ValidationError:

                errors.append("Please enter a valid email address.")

        # ---------------------------------------------
        # Duplicate account checks
        # ---------------------------------------------

        if username and User.objects.filter(username__iexact=username).exists():

            errors.append("This username is already registered.")

        if email and User.objects.filter(email__iexact=email).exists():

            errors.append("This email address is already registered.")

        # ---------------------------------------------
        # Tailor validation
        # ---------------------------------------------

        if role == "Tailor":

            if not shop_name:

                errors.append("Shop name is required.")

            try:

                validate_registration_document(trade_license)

            except ValidationError as exc:

                errors.extend(exc.messages)

        # ---------------------------------------------
        # Rider validation
        # ---------------------------------------------

        if role == "Rider":

            if vehicle_type not in {
                "Motorcycle",
                "Bicycle",
                "Car",
            }:

                errors.append("Please select a valid vehicle type.")

            try:

                validate_registration_document(driving_license)

            except ValidationError as exc:

                errors.extend(exc.messages)

        # ---------------------------------------------
        # Return to registration if validation fails
        # ---------------------------------------------

        if errors:

            for error in errors:

                messages.error(request, error)

            return render(
                request,
                "core/register.html",
                {
                    "selected_role": role,
                },
            )

        # ---------------------------------------------
        # Prepare user information
        # ---------------------------------------------

        names = full_name.split(maxsplit=1)

        first_name = names[0]

        last_name = names[1] if len(names) > 1 else ""

        # ---------------------------------------------
        # Save complete registration atomically
        # ---------------------------------------------

        with transaction.atomic():

            # Customers can log in immediately.
            # Tailors and riders require administrator approval.

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=(role == "Customer"),
            )

            # -----------------------------------------
            # Create linked user profile.
            # -----------------------------------------

            UserProfile.objects.create(
                user=user,
                role=role,
                phone=phone,
                approval_status=(
                    "Approved" if role == "Customer" else "Pending Approval"
                ),
                vehicle_type=(vehicle_type if role == "Rider" else None),
                driving_license=(driving_license if role == "Rider" else None),
            )

            # -----------------------------------------
            # Tailor shop and approval record.
            # -----------------------------------------

            if role == "Tailor":

                TailorShop.objects.create(
                    owner=user,
                    name=shop_name,
                    trade_license=trade_license,
                )

                Approval.objects.create(
                    user=user,
                    role="Tailor",
                    status="Pending",
                )

            # -----------------------------------------
            # Rider approval record.
            # -----------------------------------------

            elif role == "Rider":

                Approval.objects.create(
                    user=user,
                    role="Rider",
                    status="Pending",
                )

        # ---------------------------------------------
        # Success message
        # ---------------------------------------------

        if role == "Customer":

            messages.success(
                request, "Your account was created successfully. " "Please log in."
            )

        else:

            messages.success(
                request,
                "Registration submitted successfully. "
                "Please wait for administrator approval.",
            )

        return redirect("core:login")

    # ---------------------------------------------
    # GET: Display the registration form
    # ---------------------------------------------

    return render(
        request,
        "core/register.html",
        {
            "selected_role": selected_role,
        },
    )


# =========================================================
# PUBLIC TAILOR PAGES
# =========================================================


def tailor_list(request):

    return render(
        request,
        "core/tailor_list.html",
    )


def tailor_details(request):

    return render(
        request,
        "core/tailor_details.html",
    )


# =========================================================
# MARKETPLACE
# =========================================================


def marketplace_gallery_view(request):

    designs = Design.objects.all()

    # ---------------------------------------------
    # Search
    # ---------------------------------------------

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    if search_query:

        designs = designs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(shop__name__icontains=search_query)
        )

    # ---------------------------------------------
    # Category filtering
    # ---------------------------------------------

    category = request.GET.get(
        "category",
        "",
    ).strip()

    if category and category != "All":

        designs = designs.filter(category=category)

    # ---------------------------------------------
    # Sorting
    # ---------------------------------------------

    sort_by = request.GET.get(
        "sort",
        "newest",
    )

    if sort_by == "price_low":

        designs = designs.order_by("price")

    elif sort_by == "price_high":

        designs = designs.order_by("-price")

    elif sort_by == "rating":

        designs = designs.order_by("-rating")

    else:

        designs = designs.order_by("-created_at")

    return render(
        request,
        "core/marketplace.html",
        {
            "designs": designs,
            "search_query": search_query,
            "selected_category": category,
            "selected_sort": sort_by,
        },
    )


# =========================================================
# GALLERY
# =========================================================


def gallery_view(request):

    gallery_items = Design.objects.all().order_by("-created_at")

    return render(
        request,
        "core/gallery.html",
        {
            "gallery_items": gallery_items,
        },
    )


# =========================================================
# MARKETPLACE DESIGN DETAILS
# =========================================================


def marketplace_detail_view(request, pk):

    design = get_object_or_404(
        Design,
        pk=pk,
    )

    return render(
        request,
        "core/marketplace_detail.html",
        {
            "design": design,
        },
    )


# =========================================================
# LOGOUT
# =========================================================


def logout_view(request):

    logout(request)

    return redirect("core:home")


# from pathlib import Path

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.contrib.auth import login, logout, authenticate
# from django.contrib.auth.models import User
# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
# from django.core.validators import validate_email
# from django.db import transaction
# from django.db.models import Q

# from .models import Design, UserProfile
# from tailors.models import TailorShop
# from adminpanel.models import Approval


# # =========================================================
# # PUBLIC PAGES
# # =========================================================

# def home(request):
#     return render(request, "core/home.html")


# def gallery(request):
#     return gallery_view(request)


# def pricing(request):
#     return render(request, "core/pricing.html")


# def contact(request):
#     return render(request, "core/contact.html")


# # =========================================================
# # USER ROLE REDIRECTION
# # =========================================================

# def redirect_based_on_role(user):
#     """
#     Redirect authenticated users according to their database role.
#     Admin privileges come from Django's staff/superuser flags.
#     """

#     if user.is_staff or user.is_superuser:
#         return redirect("adminpanel:dashboard")

#     try:
#         profile = user.profile
#     except UserProfile.DoesNotExist:
#         messages.warning(
#             None,
#             "Your account profile is missing."
#         ) if False else None
#         return redirect("core:home")

#     if profile.role == "Customer":
#         return redirect("customers:dashboard")

#     if profile.role == "Tailor":
#         return redirect("tailors:dashboard")

#     if profile.role == "Rider":
#         return redirect("riders:dashboard")

#     return redirect("core:home")


# # =========================================================
# # LOGIN
# # =========================================================

# def login_view(request):

#     if request.user.is_authenticated:
#         return redirect_based_on_role(request.user)

#     selected_role = request.POST.get("role", "Customer")
#     identifier = ""

#     if request.method == "POST":

#         identifier = request.POST.get(
#             "identifier", ""
#         ).strip()

#         password = request.POST.get(
#             "password", ""
#         )

#         allowed_roles = {
#             "Customer",
#             "Tailor",
#             "Rider",
#             "Admin",
#         }

#         if selected_role not in allowed_roles:

#             messages.error(
#                 request,
#                 "Please select a valid account type."
#             )

#         elif not identifier or not password:

#             messages.error(
#                 request,
#                 "Enter your email or username and password."
#             )

#         else:

#             # ---------------------------------------------
#             # Allow login using username or email address.
#             # ---------------------------------------------

#             username = identifier

#             if "@" in identifier:

#                 matching_users = User.objects.filter(
#                     email__iexact=identifier
#                 )

#                 if matching_users.count() == 1:
#                     username = matching_users.first().username

#             user = authenticate(
#                 request,
#                 username=username,
#                 password=password,
#             )

#             if user is None:

#                 messages.error(
#                     request,
#                     "Incorrect credentials, or your account "
#                     "has not yet been activated."
#                 )

#             else:

#                 # -----------------------------------------
#                 # Read actual role from the database.
#                 # -----------------------------------------

#                 if user.is_staff or user.is_superuser:

#                     actual_role = "Admin"

#                 else:

#                     try:
#                         actual_role = user.profile.role

#                     except UserProfile.DoesNotExist:
#                         actual_role = None

#                 # -----------------------------------------
#                 # Validate selected role.
#                 # -----------------------------------------

#                 if actual_role is None:

#                     messages.error(
#                         request,
#                         "Your user profile is missing. "
#                         "Please contact an administrator."
#                     )

#                 elif actual_role != selected_role:

#                     messages.error(
#                         request,
#                         "This account does not match "
#                         "the selected login role."
#                     )

#                 else:

#                     login(request, user)

#                     return redirect_based_on_role(user)

#     return render(
#         request,
#         "core/login.html",
#         {
#             "selected_role": selected_role,
#             "identifier": identifier,
#         },
#     )


# # =========================================================
# # REGISTRATION DOCUMENT VALIDATION
# # =========================================================

# ALLOWED_DOCUMENT_EXTENSIONS = {
#     ".pdf",
#     ".jpg",
#     ".jpeg",
#     ".png",
# }

# MAX_DOCUMENT_SIZE = 5 * 1024 * 1024


# def validate_registration_document(document):
#     """
#     Basic extension and size validation.
#     Stronger file verification and private document
#     storage are required before production deployment.
#     """

#     if not document:

#         raise ValidationError(
#             "Please upload the required document."
#         )

#     extension = Path(document.name).suffix.lower()

#     if extension not in ALLOWED_DOCUMENT_EXTENSIONS:

#         raise ValidationError(
#             "Only PDF, JPG, JPEG and PNG files are accepted."
#         )

#     if document.size > MAX_DOCUMENT_SIZE:

#         raise ValidationError(
#             "The maximum document size is 5 MB."
#         )


# # =========================================================
# # REGISTER
# # =========================================================

# def register_view(request):

#     if request.user.is_authenticated:
#         return redirect_based_on_role(request.user)

#     selected_role = request.POST.get(
#         "role",
#         "Customer",
#     )

#     if request.method == "POST":

#         role = selected_role

#         # ---------------------------------------------
#         # Common registration fields
#         # ---------------------------------------------

#         full_name = request.POST.get(
#             "full_name", ""
#         ).strip()

#         username = request.POST.get(
#             "username", ""
#         ).strip()

#         email = request.POST.get(
#             "email", ""
#         ).strip()

#         phone = request.POST.get(
#             "phone", ""
#         ).strip()

#         password = request.POST.get(
#             "password", ""
#         )

#         confirm_password = request.POST.get(
#             "confirm_password", ""
#         )

#         # ---------------------------------------------
#         # Role-specific registration fields
#         # ---------------------------------------------

#         shop_name = request.POST.get(
#             "shop_name", ""
#         ).strip()

#         vehicle_type = request.POST.get(
#             "vehicle_type", ""
#         ).strip()

#         trade_license = request.FILES.get(
#             "trade_license"
#         )

#         driving_license = request.FILES.get(
#             "driving_license"
#         )

#         errors = []

#         # ---------------------------------------------
#         # Role validation
#         # ---------------------------------------------

#         if role not in {
#             "Customer",
#             "Tailor",
#             "Rider",
#         }:

#             errors.append(
#                 "Please select a valid registration role."
#             )

#         # ---------------------------------------------
#         # Required field validation
#         # ---------------------------------------------

#         if not all([
#             full_name,
#             username,
#             email,
#             phone,
#             password,
#             confirm_password,
#         ]):

#             errors.append(
#                 "Please complete all required fields."
#             )

#         # ---------------------------------------------
#         # Password validation
#         # ---------------------------------------------

#         if password != confirm_password:

#             errors.append(
#                 "Passwords do not match."
#             )

#         elif password:

#             try:

#                 validate_password(password)

#             except ValidationError as exc:

#                 errors.extend(exc.messages)

#         # ---------------------------------------------
#         # Email validation
#         # ---------------------------------------------

#         if email:

#             try:

#                 validate_email(email)

#             except ValidationError:

#                 errors.append(
#                     "Please enter a valid email address."
#                 )

#         # ---------------------------------------------
#         # Duplicate account checks
#         # ---------------------------------------------

#         if username and User.objects.filter(
#             username__iexact=username
#         ).exists():

#             errors.append(
#                 "This username is already registered."
#             )

#         if email and User.objects.filter(
#             email__iexact=email
#         ).exists():

#             errors.append(
#                 "This email address is already registered."
#             )

#         # ---------------------------------------------
#         # Tailor validation
#         # ---------------------------------------------

#         if role == "Tailor":

#             if not shop_name:

#                 errors.append(
#                     "Shop name is required."
#                 )

#             try:

#                 validate_registration_document(
#                     trade_license
#                 )

#             except ValidationError as exc:

#                 errors.extend(exc.messages)

#         # ---------------------------------------------
#         # Rider validation
#         # ---------------------------------------------

#         if role == "Rider":

#             if vehicle_type not in {
#                 "Motorcycle",
#                 "Bicycle",
#                 "Car",
#             }:

#                 errors.append(
#                     "Please select a valid vehicle type."
#                 )

#             try:

#                 validate_registration_document(
#                     driving_license
#                 )

#             except ValidationError as exc:

#                 errors.extend(exc.messages)

#         # ---------------------------------------------
#         # Return to registration if validation fails
#         # ---------------------------------------------

#         if errors:

#             for error in errors:

#                 messages.error(
#                     request,
#                     error
#                 )

#             return render(
#                 request,
#                 "core/register.html",
#                 {
#                     "selected_role": role,
#                 },
#             )

#         # ---------------------------------------------
#         # Prepare user information
#         # ---------------------------------------------

#         names = full_name.split(maxsplit=1)

#         first_name = names[0]

#         last_name = (
#             names[1]
#             if len(names) > 1
#             else ""
#         )

#         # ---------------------------------------------
#         # Save complete registration atomically
#         # ---------------------------------------------

#         with transaction.atomic():

#             # Customers can log in immediately.
#             # Tailors and riders require administrator approval.

#             user = User.objects.create_user(
#                 username=username,
#                 email=email,
#                 password=password,
#                 first_name=first_name,
#                 last_name=last_name,
#                 is_active=(role == "Customer"),
#             )

#             # -----------------------------------------
#             # Create linked user profile.
#             # -----------------------------------------

#             UserProfile.objects.create(
#                 user=user,
#                 role=role,
#                 phone=phone,

#                 approval_status=(
#                     "Approved"
#                     if role == "Customer"
#                     else "Pending Approval"
#                 ),

#                 vehicle_type=(
#                     vehicle_type
#                     if role == "Rider"
#                     else None
#                 ),

#                 driving_license=(
#                     driving_license
#                     if role == "Rider"
#                     else None
#                 ),
#             )

#             # -----------------------------------------
#             # Tailor shop and approval record.
#             # -----------------------------------------

#             if role == "Tailor":

#                 TailorShop.objects.create(
#                     owner=user,
#                     name=shop_name,
#                     trade_license=trade_license,
#                 )

#                 Approval.objects.create(
#                     user=user,
#                     role="Tailor",
#                     status="Pending",
#                 )

#             # -----------------------------------------
#             # Rider approval record.
#             # -----------------------------------------

#             elif role == "Rider":

#                 Approval.objects.create(
#                     user=user,
#                     role="Rider",
#                     status="Pending",
#                 )

#         # ---------------------------------------------
#         # Success message
#         # ---------------------------------------------

#         if role == "Customer":

#             messages.success(
#                 request,
#                 "Your account was created successfully. "
#                 "Please log in."
#             )

#         else:

#             messages.success(
#                 request,
#                 "Registration submitted successfully. "
#                 "Please wait for administrator approval."
#             )

#         return redirect(
#             "core:login"
#         )

#     # ---------------------------------------------
#     # GET: Display the registration form
#     # ---------------------------------------------

#     return render(
#         request,
#         "core/register.html",
#         {
#             "selected_role": selected_role,
#         },
#     )


# # =========================================================
# # PUBLIC TAILOR PAGES
# # =========================================================

# def tailor_list(request):

#     return render(
#         request,
#         "core/tailor_list.html",
#     )


# def tailor_details(request):

#     return render(
#         request,
#         "core/tailor_details.html",
#     )


# # =========================================================
# # MARKETPLACE
# # =========================================================

# def marketplace_gallery_view(request):

#     designs = Design.objects.all()

#     # ---------------------------------------------
#     # Search
#     # ---------------------------------------------

#     search_query = request.GET.get(
#         "q",
#         "",
#     ).strip()

#     if search_query:

#         designs = designs.filter(
#             Q(title__icontains=search_query)
#             | Q(description__icontains=search_query)
#             | Q(shop__name__icontains=search_query)
#         )

#     # ---------------------------------------------
#     # Category filtering
#     # ---------------------------------------------

#     category = request.GET.get(
#         "category",
#         "",
#     ).strip()

#     if category and category != "All":

#         designs = designs.filter(
#             category=category
#         )

#     # ---------------------------------------------
#     # Sorting
#     # ---------------------------------------------

#     sort_by = request.GET.get(
#         "sort",
#         "newest",
#     )

#     if sort_by == "price_low":

#         designs = designs.order_by(
#             "price"
#         )

#     elif sort_by == "price_high":

#         designs = designs.order_by(
#             "-price"
#         )

#     elif sort_by == "rating":

#         designs = designs.order_by(
#             "-rating"
#         )

#     else:

#         designs = designs.order_by(
#             "-created_at"
#         )

#     return render(
#         request,
#         "core/marketplace.html",
#         {
#             "designs": designs,
#             "search_query": search_query,
#             "selected_category": category,
#             "selected_sort": sort_by,
#         },
#     )


# # =========================================================
# # GALLERY
# # =========================================================

# def gallery_view(request):

#     gallery_items = Design.objects.all().order_by(
#         "-created_at"
#     )

#     return render(
#         request,
#         "core/gallery.html",
#         {
#             "gallery_items": gallery_items,
#         },
#     )


# # =========================================================
# # MARKETPLACE DESIGN DETAILS
# # =========================================================

# def marketplace_detail_view(request, pk):

#     design = get_object_or_404(
#         Design,
#         pk=pk,
#     )

#     return render(
#         request,
#         "core/marketplace_detail.html",
#         {
#             "design": design,
#         },
#     )


# # =========================================================
# # LOGOUT
# # =========================================================

# def logout_view(request):

#     logout(request)

#     return redirect(
#         "core:home"
#     )
