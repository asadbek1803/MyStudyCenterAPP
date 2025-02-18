from django.urls import path
from .views import *

urlpatterns = [
    path('', teacher_view, name='teacher_dashboard'),
    path('my/groups/', my_groups, name='my_groups_teacher'),
    path('my/group/<slug:slug>/', single_guruh_teacher, name="single_guruh_teacher"),
    path('my/notifications/', get_notification_message, name='get_notification'),
    path('my/notification/message/<str:username>/', read_message, name='get_notification_message'),
    path('my/subjects/', teacher_fan_list, name='teacher_fan_list'),

]   