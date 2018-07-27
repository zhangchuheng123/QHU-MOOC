from django import forms
from django.contrib.auth.forms import PasswordChangeForm

class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(MyPasswordChangeForm, self).__init__(*args, **kwargs)
        for field in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field].widget.attrs = {'class': 'form-control'}