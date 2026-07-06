from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    path('', views.index, name='index'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
]