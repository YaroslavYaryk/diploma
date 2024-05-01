from django.urls import path

from .views import index, dicom_to_jpeg

urlpatterns = [
    path('', index, name='index'),
    path('dicom_to_jpeg/', dicom_to_jpeg, name='dicom_to_jpeg')
]