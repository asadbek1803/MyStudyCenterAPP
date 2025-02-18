from django.db import models

# Create your models here.

class Reklamalar(models.Model):
    name = models.CharField(max_length=200)
    image = models.FileField(upload_to='images/reklamalar/')
    url = models.URLField(blank=True, null=True)
    added_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Reklamalar"
        verbose_name_plural = "Reklamalar"
        ordering = ['-added_at']  # Orders messages by the most recent first

class Services(models.Model):
    icon = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    about = models.TextField()
    
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Xizmatlar"
        verbose_name_plural = "Xizmatlar"
          # Orders messages by the most recent first

class Vacancy(models.Model):
    name = models.CharField(max_length=200)
    price = models.CharField(max_length=200)
    company = models.CharField(max_length=200, default="My Study Center")
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='vacancy/images/')
    day_time = models.CharField(max_length=200)
    about = models.TextField()
    contact = models.URLField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vakansiyalar"
        verbose_name_plural = "Vakansiyalar"
        ordering = ['-price']  # Orders messages by the most recent first

