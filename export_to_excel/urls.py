from django.urls import path
from .views import export_groups_to_excel, export_students_excel, export_fan_to_excel, import_groups, export_teachers_to_excel

urlpatterns = [
    path('guruhlar/download/', export_groups_to_excel, name='export_guruhlar'),
    path('fanlar/download/', export_fan_to_excel, name='export_fanlar'),
    path('import/groups/', import_groups, name='import_groups'),
    path('ustozlar/download/', export_teachers_to_excel, name='export_ustoz'),
    path('talabalar/download/', export_students_excel, name='talabalar_download'),
]