from django.contrib import admin
from .models import Reklamalar, Services, Vacancy
from django.contrib.admin import ModelAdmin
# Register your models here.

@admin.register(Reklamalar)
class ReklamalarAdmin(ModelAdmin):
    list_display = ('id' , 'name', 'image', 'url', 'added_at')
    list_display_links = ('id', 'name',  )
    search_fields = ('name', )


@admin.register(Services)
class ServicesAdmin(ModelAdmin):
    list_display = ('id', 'name', 'icon', 'about')
    list_display_links = ('id', 'name', )
    search_fields = ('id', 'name', )


@admin.register(Vacancy)
class VacancyAdmin(ModelAdmin):
    list_display = ('id', 'name', 'price', 'company', 'short_about', 'contact', 'is_active')
    list_display_links = ('id', 'name', )
    search_fields = ('id', 'name', )
    list_filter = ('price', 'company')


    def short_about(self, obj):
        return obj.about[:20]  # Truncate 'about' to the first 10 characters
    short_about.short_description = 'About'


# admin.site.register(Services)
# admin.site.register(Vacancy)


