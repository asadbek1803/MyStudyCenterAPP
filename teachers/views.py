from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import Account, NotifactionMessage
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models.functions import TruncDate
from django.db.models import Count
from study_center.models import Group, StudyCenter, Fanlar, AttendanceRecord


@login_required
def teacher_view(request):
    if request.user.role == 'teacher':
        teacher = request.user
        
        total_teachers = Account.objects.filter(study_center__id=teacher.study_center.id, role='teacher').count()  # faqat ustozlar soni
        total_students = Account.objects.filter(study_center__id=teacher.study_center.id, role='student').count()  # faqat o'quvchilar soni
        leave_obj = Group.objects.filter(study_center__id=teacher.study_center.id).first()
        total_subjects = Fanlar.objects.filter(study_center=request.user.study_center).count()
        # jami = total_subjects.fanlar.count()
        
        
        
        # print(jami)
        data = Account.objects.filter(study_center__id=teacher.study_center.id, role='student').annotate(date=TruncDate('date_joined')).values('date').annotate(count=Count('id')).order_by('date')
        dates = [entry['date'].strftime('%Y-%m-%d') for entry in data]
        counts = [entry['count'] for entry in data]
        # print(dates, counts)
        group_data = Group.objects.filter(study_center__id = teacher.study_center.id).annotate(student_count=Count('students')).values('name', 'student_count')
        labels = [entry['name'] for entry in group_data]
        group_data = [entry['student_count'] for entry in group_data]
        notification = NotifactionMessage.objects.filter(receiver = request.user).all().filter(is_read = False)
        
        if leave_obj == None:
            context = {
                'subject_list': Fanlar.objects.filter(teacher=teacher),
                'total_teachers': total_teachers,
                'total_students': total_students,
                'chart_url': f'{settings.MEDIA_URL}teacher_student_chart.png',
                'dates': dates,
                'counts': counts,
                'labels': labels,
                'total_leave': Account.objects.filter(role='student', study_center=request.user.study_center,
                                                      is_active=False).count(),
                'total_attendance': AttendanceRecord.objects.filter(study_center=request.user.study_center).count(),
                'group_data': group_data,
                'total_subjects': total_subjects,
                'notification_message': notification,
            
            }
            return render(request, 'teachers/dashboard.html', context=context)
            
        
        context = {
            'subject_list': Fanlar.objects.filter(teacher=teacher),
            'total_teachers': total_teachers,
            'total_students': total_students,
            'chart_url': f'{settings.MEDIA_URL}teacher_student_chart.png',
            'dates': dates,
            'counts': counts,
            'labels': labels,
            'group_data': group_data,
            'total_attendance': AttendanceRecord.objects.filter(study_center=request.user.study_center).count(),
            'total_leave':  Account.objects.filter(role='student', study_center=request.user.study_center, is_active = False).count(),
            'total_subjects': total_subjects,
            'notification_message': notification,
            
        }
        return render(request, 'teachers/dashboard.html', context=context)
    else:
        return redirect('/')

@login_required
def my_groups(request):
    if request.user.role == 'teacher':
        teacher = request.user
        groups = Group.objects.filter(study_center__id=teacher.study_center.id).filter(teachers = request.user)
        notification = NotifactionMessage.objects.filter(receiver = request.user).all().filter(is_read = False)
        context = {
            'title': "Mening guruhlarim",
            'groups': groups,
            'notification_message': notification,
        }
        return render(request, 'teachers/my_groups.html', context=context)
    else:
        return redirect('/')


@login_required
def single_guruh_teacher(request, slug):
    if request.user.role == 'teacher':
        guruh = Group.objects.filter(slug=slug).first()
        students = guruh.students.all()
        if guruh:
            students = guruh.students.all()
            student_fanlar = {student: student.fanlar.all() for student in students}
            notification = NotifactionMessage.objects.filter(receiver=request.user, is_read=False)

            # Reytinglarni hisoblash
            student_scores = [(student, student.month_score) for student in students]
            student_scores.sort(key=lambda x: x[1], reverse=True)
            top_students = student_scores[:3]  # 1, 2, va 3-o'rin
            students = guruh.students.all()

            data = {
                'guruh': guruh,
                'slug': guruh.slug,
                'teachers': guruh.teachers.all(),
                'students': students,
                'total_students': guruh.students.count(),
                'student_fanlar': student_fanlar,
                'notification_message': notification,
                'top_students': top_students,
                'top_counter': len(top_students),
                # Reytinglarni yuborish
            }
            return render(request, 'teachers/single_guruh.html', data)
    else:
        return redirect('/')
        
@login_required
def get_notification_message(request):
    if request.user.role == 'teacher':
        # Retrieve all notifications for the current user
        notifications = NotifactionMessage.objects.filter(receiver=request.user).select_related('sender')

        # Dictionary to map senders to their messages
        sender_messages = {}

        for notification in notifications:
            sender = notification.sender
            if sender not in sender_messages:
                sender_messages[sender] = []
            sender_messages[sender].append(notification.id)

        return render(request, 'teachers/bildirishnomalar.html', {
            'sender_messages': sender_messages
        })
    else:
        return render(request, 'teachers/bildirishnomalar.html', {'error': 0})
# @login_required
# def read_notification(request, id):
#     if request.user.role == 'teacher':
#         get = NotifactionMessage.objects.get(id=id)
#         get.is_read = True
#         get.save()
#         return redirect('get_notification')
#     return redirect('/')
    
@login_required
def read_message(request, username):
    if request.user.role == 'teacher':
        # Foydalanuvchini tekshirish va yuboruvchi ob'ektini olish
        sender = get_object_or_404(Account, username=username)

        # Foydalanuvchiga yuborilgan barcha xabarlarni olish va tanlangan yuboruvchidan kelgan xabarlarni olish
        notifications = NotifactionMessage.objects.filter(receiver=request.user, sender=sender)

        # Tanlangan yuboruvchidan kelgan barcha xabarlarni o'qilgan deb belgilash
        notifications.update(is_read=True)

        # Foydalanuvchiga yuborilgan barcha xabarlarni yuboruvchiga bog'lab olish
        all_notifications = NotifactionMessage.objects.filter(receiver=request.user).select_related('sender')
        
        # Yuboruvchi va ularning xabarlarini lug'atga joylash
        sender_messages = {}
        for notification in all_notifications:
            sender = notification.sender
            if sender not in sender_messages:
                sender_messages[sender] = []
            sender_messages[sender].append(notification)

        # Foydalanuvchiga xabarlar sahifasini ko'rsatish
        return render(request, 'teachers/single_message.html', {
            'selected_sender': sender,
            'notifications': notifications,
            'sender_messages': sender_messages
        })

    # Agar foydalanuvchi ustoz bo'lmasa, asosiy sahifaga qaytarish
    return redirect('/')

@login_required
def teacher_fan_list(request):
    if request.user.role != 'teacher':
        return redirect('/')

    # O'qituvchining barcha fanlarini olish
    fans = Fanlar.objects.filter(teacher=request.user)

    return render(request, 'teachers/fan_list.html', {
        'fans': fans
    })
    
