from django.urls import reverse, path
from .views import models_history_view, teachers_history, student_history

urlpatterns = [
    path('all/', models_history_view, name='all_history'),
    path('teacher/', teachers_history, name='teacher_history'),
    path('student/', student_history, name='student_history'),
]