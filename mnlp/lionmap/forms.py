from django import forms
from datetime import datetime, timedelta, time

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class DateFilterForm(forms.Form):
    start = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}, format='%d/%m/%Y'), input_formats=('%d/%m/%Y',))
    end = forms.DateField(widget=forms.DateInput(attrs={'class':'datepicker'}, format='%d/%m/%Y'), input_formats=('%d/%m/%Y',))

    def __init__(self, user, *args, **kwargs):
        super(DateFilterForm, self).__init__(*args, **kwargs)
        self.user = user

        self.helper = FormHelper()
        self.helper.form_id = 'date-range-selector'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '#'
        self.helper.add_input(Submit('submit', 'Filter'))

    def clean_start(self):
        start = self.cleaned_data['start']
        if not self.user.is_authenticated() and datetime.combine(start, time()) > (datetime.now() - timedelta(days=3)):
            raise forms.ValidationError("Last 72 hours are restricted.")

        return start


    def clean_end(self):
        end = self.cleaned_data['end']
        if not self.user.is_authenticated() and datetime.combine(end, time()) > (datetime.now() - timedelta(days=3)):
            raise forms.ValidationError("Last 72 hours are restricted.")

        return end