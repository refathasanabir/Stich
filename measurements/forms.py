from django import forms
from customers.models import MeasurementProfile


class MeasurementProfileForm(forms.ModelForm):
    class Meta:
        model = MeasurementProfile
        fields = [
            "name",
            "relation",
            "gender",
            "category",
            "chest",
            "waist",
            "shoulders",
            "sleeve_length",
            "collar",
            "height",
            "width",
            "is_default",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg"}
            ),
            "relation": forms.Select(
                attrs={"class": "w-full px-3 py-2 border rounded-lg"}
            ),
            "gender": forms.Select(
                attrs={"class": "w-full px-3 py-2 border rounded-lg"}
            ),
            "category": forms.TextInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg"}
            ),
            "chest": forms.NumberInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg", "step": "0.01"}
            ),
            "waist": forms.NumberInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg", "step": "0.01"}
            ),
            "shoulders": forms.NumberInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg", "step": "0.01"}
            ),
            "sleeve_length": forms.NumberInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg", "step": "0.01"}
            ),
            "collar": forms.NumberInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg", "step": "0.01"}
            ),
            "height": forms.NumberInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg", "step": "0.01"}
            ),
            "width": forms.NumberInput(
                attrs={"class": "w-full px-3 py-2 border rounded-lg", "step": "0.01"}
            ),
            "is_default": forms.CheckboxInput(
                attrs={"class": "rounded border-gray-300 text-navy"}
            ),
        }
