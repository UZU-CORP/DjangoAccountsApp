from django import forms

class SubmitEmailCode(forms.Form):
    code = forms.CharField(max_length=100)