from django.contrib import admin
from .models import Material, MaterialComponent, MaterialPrice, MaterialType

# Register your models here.
admin.site.register(Material)
admin.site.register(MaterialComponent)
admin.site.register(MaterialPrice)
admin.site.register(MaterialType)