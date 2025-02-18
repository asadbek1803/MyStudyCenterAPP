import calendar
import os
from accounts.models import Account
from django.http import FileResponse, Http404
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import  Reklamalar, Services, Vacancy
from study_center.models import  LessonsTable, LessonSchedule, Fanlar, Group, AttendanceRecord, Payments
from siteabout.models import Settings, Team

def role_based_redirect(request):
    if request.user.is_authenticated:
        user = request.user
        if user.role == 'student':
            return redirect('student')
        elif user.role == 'director' or user.role == 'teacher':
            return redirect('dashboard')
        elif user.is_superadmin:
            return redirect('admin')
    return redirect('login')  # Agar hech qaysi shart bajarilmasa



@login_required
def error_page(request):
    data = {
        "title": "Xatolik yuz berdi!"
    }
    return render(request, 'error.html', data)


def home(request):
    data = {
        "title": "Asosiy sahifa", 
        'services': Services.objects.all()
    }
    return render(request, 'home/index.html', data)


def vacancy_view(request):
    data = {
        "title": "Vakansiyalar",
        "vacancys": Vacancy.objects.all()
    }

    return render(request, "home/vacancy.html", data)

def about(request):
    return render(request, "home/about.html")

@login_required
def dashboard(request):
    if request.user.role == 'director':
        if request.user.study_center:
            study_center_id = request.user.study_center.id
            fanlar = Fanlar.objects.filter(teacher__study_center_id=study_center_id)
            total_students = request.user.study_center.students.count()

            # Yillar bo'yicha o'quvchilar soni
            student_counts = (
                request.user.study_center.students
                .extra(select={'year': "strftime('%%Y', date_joined)"})
                .values('year')
                .annotate(total=Count('id'))
                .order_by('year')
            )
            years = [item['year'] for item in student_counts]
            totals = [item['total'] for item in student_counts]

            # Tanlangan yilda oylar bo'yicha o'quvchilar sonini aniqlash
            selected_year = request.GET.get('year', datetime.now().year)  # Default - hozirgi yil
            monthly_counts = (
                request.user.study_center.students
                .filter(date_joined__year=selected_year)
                .extra(select={'month': "strftime('%%m', date_joined)"})
                .values('month')
                .annotate(total=Count('id'))
                .order_by('month')
            )
            months = [item['month'] for item in monthly_counts]
            monthly_totals = [item['total'] for item in monthly_counts]

            now_day = datetime.now().strftime('%A')
            if now_day == 'Monday':
                now_day = "Duyshanba"
            elif now_day == 'Tuesday':
                now_day = "Seshanba"
            elif now_day == 'Wednesday':
                now_day = "Chorshanba"
            elif now_day == 'Thursday':
                now_day = "Payshanba"
            elif now_day == 'Friday':
                now_day = "Juma"
            elif now_day == 'Saturday':
                now_day = "Shanba"
            elif now_day == 'Sunday':
                now_day = "Yakshanba"
            # Hozirgi kun nomi
            today_lessons = LessonSchedule.objects.filter(
                lesson__study_center_id=study_center_id,
                day=now_day
            )

            groups = Group.objects.filter(study_center=request.user.study_center)
            day = datetime.now().day
            messages = ["Bugun oyning birinchi sanasi, siz o'quvchilar oylik ballarini 0 ga tushiringiz kerak!"] if day == 1 else []
            data = {
                "title": "Director dashboard",
                'reklama': Reklamalar.objects.last(),
                'user': request.user,
                'lessons': today_lessons,
                'fanlar': fanlar,
                'groups': groups,
                'total_students': total_students,
                'teacher_name': request.user.first_name,
                'teacher_role': request.user.role,
                'study_center_name': request.user.study_center.name,
                'years': years,
                'total_payments': Payments.total_payments(study_center=request.user.study_center),
                'totals': totals,
                'total_attendance': AttendanceRecord.objects.filter(study_center=request.user.study_center).count(),
                'total_leaves': Account.objects.filter(role='student', study_center=request.user.study_center, is_active=False).count(),
                'total_subjects': Fanlar.objects.filter(study_center=request.user.study_center).count(),
                'months': months,
                'monthly_totals': monthly_totals,
                'selected_year': selected_year,
                'messages': messages
            }
            return render(request, 'dashboard/dashboard.html', data)
        else:
            return render(request, 'dashboard/dashboard.html')

    elif request.user.role == 'teacher':
        return redirect(reverse('teacher_dashboard'))

    return redirect('base_url')


def app_download(request):
    # Settings modelidan birinchi qatorni olamiz
    settings = get_object_or_404(Settings)

    # Fayl yo'liga kiramiz
    file_path = settings.android_file.path

    # Agar fayl mavjud bo'lsa, yuklab olish uchun yuboramiz
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    else:
        raise Http404("Fayl topilmadi.")


def team(request):
    data = {
        'teams': Team.objects.all()
    }
    return render(request, "home/team.html", data)




@login_required
def arxiv(request):
    return render(request, '360-video.html')