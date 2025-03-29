from django import forms

# TODO
# class ReportAirborneForm(forms.Form):
#     report_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
#     report_illness = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter detailed report here.', 'style': 'height: 220px;', 'class': 'form-control'}))
#     report_symptom_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

     # def cleaned_data(self):
     #    cleaned_data = super().clean()
     #    file = cleaned_data.get("report_file")
     
     #    if form.is_valid():