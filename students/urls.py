from django.urls import path
from .views import dashboard, exams_list,  my_study_center, groups_view, group_rating_view, my_attendance_view, exam_results_view

urlpatterns = [
    path('dashboard/', dashboard, name='student'),
    path('my/study_center/', my_study_center, name='my_study_center'),
    path('my/groups/', groups_view, name='my_groups'),
    path('my/group/rating/<slug:slug>/', group_rating_view, name='group_rating'),
    path('my/attendance/', my_attendance_view, name='my_attendance_student'),
    path('my/statistics/', exam_results_view, name="exam_results_student"),
    path('my/exams/', exams_list, name='exams_list_student')
]