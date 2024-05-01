from django.urls import path

from .views import MaterialSelectorView, SelectMaterialForCustomer

urlpatterns = [
    path('', MaterialSelectorView.as_view(), name="material-selector"),
    path('select-material/', SelectMaterialForCustomer.as_view(), name="select-material")
]
