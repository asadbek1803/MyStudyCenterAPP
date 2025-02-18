from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
from study_center.models import LessonSchedule, Attendance, AttendanceRecord, StudyCenter, Fanlar, Group
from django.db.models import Count, Case, When, IntegerField
from imtihonlar.models import  Imtihonlar, StudentResult
from accounts.models import NotifactionMessage
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
@login_required
def dashboard(request):
    if request.user.role == 'student':
        today = datetime.now().weekday()

        # Keyingi 7 kun uchun dars jadvalini olish
        next_7_days = []
        for i in range(7):
            day = (today + i) % 7
            day_name = ['Duyshanba', 'Seshanba', 'Chorshanba', 'Payshanba', 'Juma', 'Shanba', 'Yakshanba'][day]
            date = (datetime.now() + timedelta(days=i)).date()

            # Ushbu kun uchun darslarni olish
            lessons = LessonSchedule.objects.filter(
                lesson__group__students=request.user,
                day=day_name
            ).order_by('time')

            next_7_days.append({
                'date': date,
                'day': day_name,
                'lessons': lessons
            })

        # Davomat foizini hisoblash
        total_attendances = Attendance.objects.filter(student=request.user).count()
        present_attendances = Attendance.objects.filter(student=request.user, is_present=True).count()

        attendance_percentage = 0
        if total_attendances > 0:
            attendance_percentage = (present_attendances / total_attendances) * 100

        latest_results = StudentResult.objects.filter(student=request.user).order_by('-exam__date')[:5]

        # Kelgusi imtihonlarni olish
        upcoming_exams = Imtihonlar.objects.filter(
            students=request.user,
            date__gte=datetime.now().date()
        ).order_by('date')[:3]

        # Kelgusi topshiriqlar
        # upcoming_assignments_list = Assignment.objects.filter(
        #     student=request.user,
        #     due_date__gte=timezone.now()
        # ).order_by('due_date')

        # Yangi xabarlar
        notifications_list = NotifactionMessage.objects.filter(
            receiver=request.user
        ).order_by('-sending_date')[:5]

        data = {
            'title': "O'quvchi boshqaruv paneli",
            'total_courses': request.user.fanlar.count(),
            'schedule': next_7_days,
            'attendance_percentage': round(attendance_percentage, 2),
            'latest_results': latest_results,
            'upcoming_exams': upcoming_exams,
            'notifications_list': notifications_list,
        }
        return render(request, 'students/dashboard.html', data)
    return redirect('login')




@login_required
def my_study_center(request):
    if request.user.role != 'student':
        return redirect('block_error_page')

    data = {
        'title': "Mening o'quv markazim",
        'study_center': request.user.study_center,
        'courses': Fanlar.objects.filter(study_center=request.user.study_center),

    }

    return render(request, 'students/my-study-center.html', data)



@login_required
def groups_view(request):
    if request.user.role == 'student':

        return render(request, 'students/groups-list.html', {'groups': request.user.groups.all()})
    else:
        return redirect('block_error_page')


@login_required
def group_rating_view(request, slug):
    if request.user.role == 'student':
        group = get_object_or_404(Group, slug=slug, study_center = request.user.study_center)

        # Guruhdagi o'quvchilarni va reytingni olish
        students = group.students.all()
        sorted_students = sorted(students, key=lambda x: x.month_score, reverse=True)
        ratings = {student: rank for rank, student in enumerate(sorted_students, start=1)}

        user_rank = ratings.get(request.user, None)

        return render(request, 'students/group-rating.html', {
            'group': group,
            'ratings': ratings,
            'user_rank': user_rank,
        })
    else:
        return redirect('block_error_page')


# @login_required
# def my_attendance_view(request):
#     if request.user.role == 'student':
#         student = request.user
#         user_groups = Group.objects.filter(students=student)
# 
#         # Attendance ma'lumotlarini olish
#         attendances = Attendance.objects.filter(student=student).select_related('lesson_schedule', 'lesson_schedule__lesson')
# 
#         # Guruh bo'yicha davomatlarni ajratish
#         group_attendances = {}
#         for group in user_groups:
#             # LessonSchedule orqali guruh bilan bog'langan davomatlarni filtrlaymiz
#             group_attendances[group] = attendances.filter(lesson_schedule__lesson__group=group)
# 
#         return render(request, 'students/my-attendance.html', {
#             'group_attendances': group_attendances
#         })
#     else:
#         return redirect('block_error_page')


@login_required
def my_attendance_view(request):
    if request.user.role == 'student':
        # Foydalanuvchini olish
        student = request.user

        # Bugungi sanani olish va o'tgan 30 kunlik oraliqni hisoblash
        today = timezone.now().date()
        one_month_ago = today - timedelta(days=30)

        # O'tgan bir oylik davomatni olish
        attendances = Attendance.objects.filter(student=student, date__range=[one_month_ago, today])

        # Umumiy darslar sonini va kelmagan kunlar sonini aniqlash
        total_classes = attendances.count()
        missed_classes = attendances.filter(is_present=False).count()

        # Foizlarni hisoblash
        if total_classes > 0:
            attended_percentage = ((total_classes - missed_classes) / total_classes) * 100
            missed_percentage = (missed_classes / total_classes) * 100
        else:
            attended_percentage = 0
            missed_percentage = 0

        context = {
            'attendances': attendances,
            'total_classes': total_classes,
            'missed_classes': missed_classes,
            'attended_percentage': attended_percentage,
            'missed_percentage': missed_percentage,
        }

        return render(request, 'students/my-attendance.html', context)

    else:
        return redirect("block_error_page")

@login_required
def exam_results_view(request):
    if request.user.role != 'student':
        return redirect("block_error_page")
    # Hozirgi oy uchun imtihonlarni olish
    current_month = datetime.now().month
    current_year = datetime.now().year
    exams = Imtihonlar.objects.filter(date__month=current_month, date__year=current_year)

    # Faqat joriy foydalanuvchining natijalarini olish
    results_data = []
    total_score = 0

    for exam in exams:
        result = StudentResult.objects.filter(exam=exam, student=request.user).first()
        if result:
            total_score += result.total_score
            results_data.append({
                'exam_name': exam.name,
                'score': result.total_score,
                'date': exam.date,
            })

    context = {
        'results_data': results_data,
        'total_score': total_score,
        'exams': exams,
    }

    return render(request, 'students/exam_results.html', context)

@login_required
def exams_list(request):
    # Hozirgi vaqtni olish

    now = timezone.now()

    # Bo'layotgan va tugagan imtihonlarni olish
    ongoing_exams = Imtihonlar.objects.filter(date__gte=now.date()).order_by('date', 'start_time')
    completed_exams = Imtihonlar.objects.filter(date__lt=now.date()).order_by('-date')

    # O'quvchining ro'yxatdan o'tganligini tekshirish
    for exam in ongoing_exams:
        exam.is_registered = exam.students.filter(id=request.user.id).exists()

    context = {
        'ongoing_exams': ongoing_exams,
        'completed_exams': completed_exams,
    }

    return render(request, 'students/exams.html', context)