# from django import forms
# from customers.models import MeasurementProfile


# class MeasurementProfileForm(forms.ModelForm):
#     class Meta:
#         model = MeasurementProfile
#         # We removed the hardcoded fields and replaced them with our JSON 'values' field
#         fields = ["name", "relation", "gender", "category", "values", "is_default"]

#         widgets = {
#             "name": forms.TextInput(
#                 attrs={"class": "w-full rounded-lg border border-gray-300 px-3 py-2"}
#             ),
#             "relation": forms.Select(
#                 attrs={"class": "w-full rounded-lg border border-gray-300 px-3 py-2"}
#             ),
#             "gender": forms.Select(
#                 attrs={"class": "w-full rounded-lg border border-gray-300 px-3 py-2"}
#             ),
#             "category": forms.TextInput(
#                 attrs={"class": "w-full rounded-lg border border-gray-300 px-3 py-2"}
#             ),
#             "values": forms.Textarea(
#                 attrs={
#                     "class": "w-full rounded-lg border border-gray-300 px-3 py-2",
#                     "rows": 4,
#                     "placeholder": '{"Chest": "40", "Shoulder": "18"}',
#                 }
#             ),
#             "is_default": forms.CheckboxInput(attrs={"class": "accent-navy h-4 w-4"}),
#         }
