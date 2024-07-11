from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'home'

router = DefaultRouter()
router.register(r'firmware', views.FirmwareViewSet)


urlpatterns = [
    path('rfids/', views.CardsCreateList.as_view(), name='api'),
    path('firmware/', views.CheckFirmware.as_view(), name='car_manage')
]