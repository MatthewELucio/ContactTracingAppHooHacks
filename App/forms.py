from django import forms
from .models import PhysicalReport2, AirborneReport3, Disease
from django.forms import DateTimeInput
from django.contrib.auth import get_user_model


User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class PhysicalReportForm2(forms.ModelForm):
    class Meta:
        model = PhysicalReport2
        fields = ['disease']

    disease = forms.ChoiceField(
        choices=Disease.objects.values_list('name', 'name').filter(disease_type=Disease.PHYSICAL),
        label = "Disease"
    )
    
    
class NameForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="First Name")
    last_name = forms.CharField(max_length=50, label="Last Name")

class AirborneReportForm3(forms.ModelForm):
    class Meta:
        model = AirborneReport3
        fields = ['symptoms_appeared_date', 'diagnosis_date', 'disease', 'was_diagnosed']

    symptoms_appeared_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="When did your symptoms start?"
    )
    
    diagnosis_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="When were you diagnosed?"
    )
    
    disease = forms.ModelChoiceField(
        queryset=Disease.objects.all().filter(disease_type=Disease.AIR),
        label="Disease"
    )
    
    was_diagnosed = forms.BooleanField(
        required=True,
        label="Diagnosed?",
        initial=False
    )