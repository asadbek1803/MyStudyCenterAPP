from django.urls import path,  re_path
from .views import create_exam, register_for_exam, get_students_by_group,  add_student_result, exam_list,exam_detail, get_student_subjects

urlpatterns = [
    path('create/study_center/new/', create_exam, name="create_exam"),
    re_path(r'^registration/study_center/(?P<exam_token>[0-9a-fA-F-]+)/$', register_for_exam, name='signup_exam'),
    path('list/', exam_list, name="exams_list"),
    re_path(r'^detail/study_center/(?P<exam_token>[0-9a-fA-F-]+)/$', exam_detail, name="exam_detail"),
    path('add/result/', add_student_result, name="add_result"),
    path('get-student-subjects/<int:student_id>/', get_student_subjects, name='get_student_subjects'),
    path('get-students-by-group/<int:group_id>/',get_students_by_group, name='get_students_by_group')

    # path('registration/exam/study_center/<str:exam_token>/', register_for_exam, name='signup_exam')

]