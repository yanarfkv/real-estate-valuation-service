from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/settings', views.settings_view, name='settings'),
    path('predict/', views.predict_and_save, name='predict'),
    path('predict/<int:property_id>/', views.appraisal_view, name='display_prediction'),
]
