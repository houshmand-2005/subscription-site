from django import forms
from .models import GenKey


class GenKeyForm(forms.ModelForm):
    class Meta:
        model = GenKey
        fields = ["subtype", "phonenumber"]
