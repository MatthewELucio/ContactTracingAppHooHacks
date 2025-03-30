from django import forms
from .models import PhysicalReport
from django.forms import DateTimeInput

class PhysicalReportForm(forms.ModelForm):
     class Meta:
        model = PhysicalReport
        fields = ['name', 'symptoms_appeared_date', 'diagnosis_date', 'symptoms', 'illness', 'was_diagnosed']
        
     name = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter description here'}),
        label="Symptoms?"
    )

     symptoms_appeared_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Start Time"
    )
    
     diagnosis_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="End Time"
    )

     symptoms = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter description here'}),
        label="Symptoms?"
    )

     illness = forms.ChoiceField(
        choices=[
            ('mono', 'Mono'),
            ('hfm', 'Hand-Foot-Mouth Disease'),
            ('other', 'Other')
        ],
        label = "Illness"
    )
    
     was_diagnosed = forms.BooleanField(
        required=True,
        label="Diagnosed?",
        initial=False
    )
