from typing import Iterable
from django.db import models

from helper import image_classification

class Collection(models.Model):
    user_ip = models.CharField(max_length=100)
    image_base64 = models.TextField()
    image = models.ImageField(upload_to='non-converted/', null=True)
    created_at = models.DateTimeField(auto_now=True)
    
    
    def save(self, *args, **kwargs) -> None:
        
        if not self.pk:
            image = self.image_base64
            
            try:
                # get image type (side, top, distant_top)
                first_layer_result = image_classification.get_image_type(image)
                
                # get image classification (healthy, sick) 
                second_layer_result = image_classification.get_image_classification(first_layer_result, image)
                
                third_layer = None
                
                if second_layer_result == "sick":
                    third_layer = image_classification.get_sickness_classification(first_layer_result, image)
                    
                
                CollectionStats.objects.create(
                    collection=self,
                    image_type=first_layer_result,
                    health_status=second_layer_result,
                    sickness=third_layer
                )
            except:
                pass
        
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Collection from {self.user_ip}"
    
    

class CollectionStats(models.Model):
    
    TOP = 'top'
    SIDE = 'side'
    
    IMAGE_TYPE_CHOICES = (
        (TOP, 'Top'),
        (SIDE, 'Side'),
    )
    
    SICK = 'sick'
    HEALTHY = 'healthy'
    
    HEALTH_STATUS_CHOICES = (
        (SICK, 'Sick'),
        (HEALTHY, 'Healthy')
    )
    
    ARTRITUS = 'artritus'
    BURSITUS = 'bursitus'
    NECROZ = 'necroz'
    OASTEOARTRITUS = 'oasteoartritus'
    PHZ = 'phz'
    REVMA_ARTHRITUS = 'revma_arthritus'
    ROZRYV_MENISKA = 'rozryv_meniska'
    TENDITIT = 'tenditit'
    
    SICKNESS_CHOICES = (
        (ARTRITUS, 'Artritus'),
        (BURSITUS, 'Bursitus'),
        (NECROZ, 'Necroz'),
        (OASTEOARTRITUS, 'Oasteoartritus'),
        (PHZ, 'Phz'),
        (REVMA_ARTHRITUS, 'Revma_arthritus'),
        (ROZRYV_MENISKA, 'rozryv_meniska'),
        (TENDITIT, 'Tenditit'),
    )
    
    
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    
    image_type = models.CharField(choices=IMAGE_TYPE_CHOICES, blank=True, null=True, max_length=10)
    
    health_status = models.CharField(choices=HEALTH_STATUS_CHOICES, blank=True, null=True, max_length=10)
    
    sickness = models.CharField(choices=SICKNESS_CHOICES, blank=True, null=True, max_length=20)