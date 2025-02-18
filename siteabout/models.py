from django.db import models

# Create your models here.
class Settings(models.Model):
    base_url = models.URLField(blank=True, null=True)
    favicon = models.FileField(upload_to='images/settings/favicon/', blank=True, null=True)
    logo = models.FileField(upload_to='images/settings/logo/', blank=True, null=True)
    support_1 = models.URLField(blank=True, null=True)
    support_2 = models.URLField(blank=True, null=True)
    site_year = models.CharField(max_length=20)
    android_app_download_url = models.URLField(blank=True, null=True)
    android_file = models.FileField(upload_to='apps/file/')
    
    def __str__(self):
        return self.site_year



class Links(models.Model):
    update_name = models.CharField(max_length=120)
    year = models.CharField(max_length=40)
    twitter = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    gmail = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.update_name




class Team(models.Model):
    full_name = models.CharField(max_length=200)
    profile_image = models.ImageField(upload_to='team/images/')
    work_title = models.TextField()
    facebook_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.full_name



    