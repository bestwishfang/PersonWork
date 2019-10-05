from django import forms


class Register(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(max_length=32)
    username = forms.CharField(max_length=32)
    # phone_number = forms.CharField(max_length=32)
    # gender = forms.CharField(max_length=32)
    # age = forms.IntegerField()
    # photo = forms.ImageField()
    # address = forms.Textarea()

