import numpy as np
from django.contrib import messages

from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt

from .forms import RegisterForm, CustomAuthenticationForm, PropertyForm
from .models import Property
from .predictors import PredictionService
from .services import get_geocode_data, get_nearby_amenities


@csrf_exempt
@require_http_methods(["POST"])
def predict_and_save(request):
    form = PropertyForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        geocode_data = get_geocode_data(data['address'])
        if not geocode_data:
            messages.error(request, 'Недействительный адрес')
            return redirect('index')
        try:
            amenities = get_nearby_amenities(float(geocode_data['lat']), float(geocode_data['lon']))
            features = [
                data['rooms'], geocode_data['address']['city'], geocode_data['address'].get('city_district', ''),
                geocode_data['address']['state'], np.log1p(data['floor']), data['housing_type'], data['house_type'],
                data['repair'], np.log1p(data['total_area']), amenities.get('schools', 0),
                amenities.get('grocery_stores', 0), amenities.get('kindergartens', 0), amenities.get('hospitals', 0)
            ]
            print(features)
            prediction_value = PredictionService.make_prediction(features)

            property_instance = Property(
                user=request.user if request.user.is_authenticated else None,
                address=data['address'],
                lat=geocode_data.get('lat', ''),
                lon=geocode_data.get('lon', ''),
                rooms=data['rooms'],
                floor=data['floor'],
                housing_type=data['housing_type'],
                total_area=data['total_area'],
                repair=data['repair'],
                house_type=data['house_type'],
                city=geocode_data['address']['city'],
                state=geocode_data['address']['state'],
                city_district=geocode_data['address'].get('city_district', ''),
                schools=amenities.get('schools', 0),
                grocery_stores=amenities.get('grocery_stores', 0),
                kindergartens=amenities.get('kindergartens', 0),
                hospitals=amenities.get('hospitals', 0),
                prediction=prediction_value
            )
            property_instance.save()
            return redirect(f'/predict/{property_instance.id}')

        except Exception as e:
            messages.error(request, f'Произошла ошибка: {e}')
            return redirect('index')
    else:
        for field in form.errors:
            form[field].field.widget.attrs['class'] += ' is-invalid'
        return render(request, 'index.html', {'form': form})


def appraisal_view(request, property_id):
    property_ = get_object_or_404(Property, pk=property_id)
    property_.prediction = '{:,.0f}'.format(property_.prediction).replace(',', ' ')

    return render(request, 'appraisal.html', {'property': property_})


def index_view(request):
    form = PropertyForm()
    return render(request, "index.html", {'form': form})


def profile_view(request):
    current_user = request.user
    properties = Property.objects.filter(user_id=current_user.id)
    for property_ in properties:
        property_.prediction = '{:,.0f}'.format(property_.prediction).replace(',', ' ')
        if len(property_.address) > 60:
            property_.address = property_.address[:60] + '...'

    return render(request, "profile.html", {'properties': properties})


def settings_view(request):
    return render(request, "settings.html")


def logout_view(request):
    logout(request)
    return redirect('index')


def register_view(response):
    if response.method == "POST":
        form = RegisterForm(response.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else:
        form = RegisterForm()

    return render(response, "registration/register.html", {"form": form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'registration/login.html'
