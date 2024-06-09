from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control',
                'placeholder': ''
            })


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                              'placeholder': 'Пароль'}))


class PropertyForm(forms.Form):
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес', 'id': 'address'}))
    total_area = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Площадь', 'id': 'total_area'}))
    rooms = forms.ChoiceField(choices=[('0', 'Студия'), ('1', '1-комнатная'), ('2', '2-комнатная'), ('3', '3-комнатная'), ('4', '4+ комнат')], widget=forms.Select(attrs={'class': 'form-control select2-search-hide'}))
    housing_type = forms.ChoiceField(choices=[('2', 'Новостройка'), ('1', 'Вторичное жилье')], widget=forms.RadioSelect(attrs={'class': 'btn-check'}))
    repair = forms.ChoiceField(choices=[('1', 'Дизайнерский ремонт'), ('2', 'Евроремонт'), ('3', 'Косметический')], widget=forms.Select(attrs={'class': 'form-control select2-search-hide'}))
    floor = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Этаж', 'id': 'floor'}))
    house_type = forms.ChoiceField(choices=[('1', 'Кирпичный'), ('3', 'Монолитный'), ('4', 'Панельный'), ('5', 'Блочный')], widget=forms.Select(attrs={'class': 'form-control select2-search-hide'}))
