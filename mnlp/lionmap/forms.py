from django import forms
from datetime import datetime, timedelta, time


class DateFilterForm(forms.Form):
    start = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}, format='%d/%m/%Y'), input_formats=('%d/%m/%Y',))
    end = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}, format='%d/%m/%Y'), input_formats=('%d/%m/%Y',))

    def clean_start(self):
        start = self.cleaned_data['start']
        if datetime.combine(start, time()) > (datetime.now() - timedelta(days=1)):
            raise forms.ValidationError("Last 24 hours are restricted.")

        return start


    def clean_end(self):
        end = self.cleaned_data['end']
        if datetime.combine(end, time()) > (datetime.now() - timedelta(days=1)):
            raise forms.ValidationError("Last 24 hours are restricted.")

        return end