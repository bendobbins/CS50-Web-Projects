from django import forms

class ProfileImageForm(forms.Form):
    image = forms.ImageField()