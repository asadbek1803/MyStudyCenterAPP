from django.urls import path
from .views import send_payment_reminder, delete_student, attendance_select_view, take_attendance, all_month_score_zero, today_lessons_view, lessons_update, lessons_delete, lesson_create, payment_summary, create_payment, edit_fan, check_payments, add_study_center, lessons_list, edit_student, leave_teacher, add_student, fanlar, delete_fan, leave_student, add_fan, get_students, download_credits, guruhlar, delete_guruh, edit_teacher, add_guruh, single_guruh, teachers_view, add_teacher, delete_teacher



urlpatterns = [
    path('add/study_center/', add_study_center, name='add_center'),
    # O'quv markaz qo'shish
    path('fanlar/', fanlar, name='fanlar'),
    path('delete/fan/<str:fan_nomi>/', delete_fan, name='delete_fan'),
    path('add/fan/', add_fan, name='add_fan'),
    path('edit/fan/<int:fan_id>/', edit_fan, name='edit_fan'),
    # Fanlar URLS 
    path('guruhlar/',  guruhlar, name='guruhlar'),
    path('delete/guruh/<str:guruh_nomi>/', delete_guruh, name='delete_guruh'),
    path('add/guruh/', add_guruh, name='add_guruh'),
    path('guruhlar/<slug:slug>/', single_guruh, name='single_guruh'),
    # Guruhlar URLS
    path('teachers/', teachers_view, name='teachers'),
    path('delete/teacher/<str:username>/', delete_teacher, name='delete_teacher'),
    path('add/teacher/', add_teacher, name='add_teacher'),
    path('edit/teacher/<str:username>/', edit_teacher, name='edit_teacher'),
    path('download/credits/teacher/<str:username>/', download_credits, name='download_credits'),
    path('teacher/exit/study_center/<str:username>/', leave_teacher, name='exit_teacher'),
    # Teachers URLS
    path('students/', get_students, name='students'),
    path('student/exit/study_center/<str:student_username>/', leave_student, name='exit_student'),
    path('add/student/', add_student, name='add_student'),
    path('edit/student/<str:username>/', edit_student, name='edit_student'),
    path('delete/student/<str:username>/', delete_student, name='delete_teacher'),
    # Students URLS
    
    path('lessons/', lessons_list, name='lessons'),
    path('check/payments/', check_payments, name='check_payments'),
    path('send_payment_reminder/', send_payment_reminder, name='send_payment_reminder'),
    path('student/pay/<str:user_id>/', create_payment, name='create_payment'),
    path('payment-summary/<str:user_id>/', payment_summary, name='payment_summary'),
    path('lesson/table/create/', lesson_create, name='lesson_create'),
    path('lesson/table/delete/<int:pk>/', lessons_delete, name='lesson_delete'),
    path('lesson/table/update/<int:pk>/', lessons_update, name='lessons_update'),
    path('attendance/group/<slug:group_slug>/', take_attendance, name='attendance'),
    path('attendance/groups/', today_lessons_view, name='today_lessons_view'),
    path('attendance/view/group/', attendance_select_view, name='attendance_select_view'),
    path('all/students/score/zero/', all_month_score_zero, name='students_score_zero')
    
    
    
    
    
    
    

   
]