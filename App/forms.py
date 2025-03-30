from django import forms
from .models import PhysicalReport2, AirborneReport, Disease
from django.forms import DateTimeInput

class PhysicalReportForm2(forms.ModelForm):
    class Meta:
        model = PhysicalReport2
        fields = ['disease']

    disease = forms.ChoiceField(
        choices=Disease.objects.values_list('name', 'name'),
        label = "Disease"
    )
    
    # was_diagnosed = forms.BooleanField(
    #     # required=True,
    #     label="Diagnosed?",
    #     initial=False
    # )
    
class NameForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")

class AirborneReportForm(forms.ModelForm):
    class Meta:
        model = AirborneReport
        fields = ['symptoms', 'symptoms_appeared_date', 'diagnosis_date', 'illness', 'was_diagnosed']
        
    symptoms = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter description here'}),
        label="Symptoms?"
    )

    symptoms_appeared_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="When did your symptoms start?"
    )
    
    diagnosis_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="When were you diagnosed?"
    )

    illness = forms.ChoiceField(
        choices=[
            ('cc', 'Commonn Cold'),
            ('flu', 'Influenza (Flu)'),
            ('other', 'Other')
        ],
        label = "Illness"
    )
    
    was_diagnosed = forms.BooleanField(
        required=True,
        label="Diagnosed?",
        initial=False
    )