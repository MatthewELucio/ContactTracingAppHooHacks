# from django import forms
# from .models import PhysicalReport, Disease
# from django.forms import DateTimeInput

# # You can create this in your view (or import it from a separate module if preferred)
# from django.forms import formset_factory

# class PhysicalReportForm(forms.ModelForm):
#     class Meta:
#         model = PhysicalReport
#         fields = ['illness', 'first_name', 'last_name']

#     illness = forms.ChoiceField(
#         # choices=[ #todo: populate from table
#         #     ('mono', 'Mono'),
#         #     ('hfm', 'Hand-Foot-Mouth Disease'),
#         #     ('other', 'Other')
#         # ],
#         choices=Disease.objects.values_list('id', 'name'),
#         label = "Disease"
#     )
    
#     # users = forms.ModelChoiceField(
#     first_name =forms.CharField(max_length=100),
#     last_name =forms.CharField(max_length=100),
        
# class PersonForm(forms.Form):
#     first_name = forms.CharField(max_length=100)
#     last_name = forms.CharField(max_length=100)
    
# PersonFormSet = formset_factory(PersonForm, extra=1)  # starts with one empty form


from django import forms
from .models import PhysicalReport
from django.forms import formset_factory


class PhysicalReportForm(forms.ModelForm):
    # Populate the choices from the Disease model.
    illness = forms.ChoiceField(
        choices=[],  # We’ll populate this in __init__
        label="Disease"
    )
    
    class Meta:
        model = PhysicalReport
        fields = ['illness']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices from the Disease table.
        from .models import Disease  # Import here to avoid circular imports if needed.
        self.fields['illness'].choices = Disease.objects.values_list('id', 'name')

class PersonForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)

PersonFormSet = formset_factory(PersonForm, extra=1)
