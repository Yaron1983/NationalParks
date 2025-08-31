# parks/forms.py
from django import forms
from .models import Park, Rating

class ParkForm(forms.ModelForm):
    class Meta:
        model = Park
        fields = ['name', 'description', 'location', 'country', 'region', 'image']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }