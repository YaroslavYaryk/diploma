from django.db import models

class Collection(models.Model):
    user_ip = models.CharField(max_length=100)
    image_base64 = models.TextField()
    image = models.ImageField(upload_to='non-converted/', null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Collection from {self.user_ip}"