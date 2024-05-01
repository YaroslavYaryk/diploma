from django.db import models

# Create your models here.

class MaterialType(models.Model):
    
    name = models.CharField(max_length=20)
    
    
    def __str__(self):
        return self.name
    
    
    

class MaterialComponent(models.Model):
    
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name




class Material(models.Model):
    
    name = models.CharField(max_length=50)
    material_type = models.ForeignKey(MaterialType, on_delete=models.CASCADE, related_name="materials")
    material_component = models.ManyToManyField(MaterialComponent, related_name="materials")

    bio_compatibility = models.IntegerField(verbose_name="Біосумісність")
    strength_durability = models.IntegerField(verbose_name="Міцність і довговічність")
    wear_resistance = models.IntegerField(verbose_name="Зносостійкість")
    elasticity_modulus = models.IntegerField(verbose_name="Модуль пружності")
    corrosion_resistance = models.IntegerField(verbose_name="Стійкість до корозії")
    
    def __str__(self):
        return self.name



class MaterialPrice(models.Model):
    
    material1 = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="material1")
    material2 = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="material2")
    price = models.BigIntegerField()
    
    def __str__(self):
        return f"{self.material1.name} + {self.material2.name} -> {self.price}"