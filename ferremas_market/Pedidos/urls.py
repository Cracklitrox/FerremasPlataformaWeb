from django.urls import path
from . import views

urlpatterns = [
    path('api/update-stock/', views.actualizar_stock, name='actualizar_stock'),
]