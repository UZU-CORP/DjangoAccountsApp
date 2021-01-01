from django import forms

class SubmitEmailCode(forms.Form):
    code = forms.CharField(max_length=100)

class PasswordResetCodeForm(forms.Form):
    code = forms.CharField()
    signature = forms.CharField()
    new_password = forms.CharField()

class PasswordChangeForm(forms.Form):
    new_password = forms.CharField()
    old_password =  forms.CharField()