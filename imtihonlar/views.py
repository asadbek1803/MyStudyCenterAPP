import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import Imtihonlar, ExamFan, StudentResult
from accounts.models import Account
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from study_center.models import StudyCenter, Group
from datetime import datetime, date, timedelta
from .forms import StudentResultForm
from django.http import JsonResponse


# Create your views here.
# Imtihon yaratish view
def create_exam(request):
    if request.user.role in ['teacher', 'director']:
        study_center = request.user.study_center

        if request.method == 'POST':
            # Formadan ma'lumotlarni olish
            exam_name = request.POST.get('exam_name')
            exam_date = request.POST.get('exam_date')  # Imtihon sanasini olish
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            # Sanani va vaqtlari to'g'riligi tekshirish
            try:
                exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
                start_time_obj = datetime.strptime(start_time, '%H:%M').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            except ValueError:
                messages.error(request, 'Sana yoki vaqt formatida xato bor.')
                return redirect('create_exam')

            # Imtihon sanasi o'tgan kunlarga kiritilmasligi kerak
            if exam_date_obj < date.today():
                messages.error(request, 'Imtihon sanasi o\'tgan kunlarga kiritilishi mumkin emas.')
                return redirect('create_exam')

            # Vaqtlar to'g'riligi
            if start_time_obj >= end_time_obj:
                messages.error(request, 'Boshlanish vaqti tugash vaqtidan oldin bo\'lishi kerak.')
                return redirect('create_exam')

            # Eski fanlar va yangi fanlarni olish
            fan_names = request.POST.getlist('fan_name')
            fan_scores = request.POST.getlist('fan_score')

            # Eski fanlar mavjudligini tekshirish
            existing_fans = ExamFan.objects.filter(study_center=study_center, name__in=fan_names)

            if existing_fans.exists():
                # Agar eski fanlar mavjud bo'lsa, foydalanuvchiga tanlov beriladi: yangilash yoki almashtirish
                if 'replace_fans' in request.POST:  # Fanlarni o'chirib, yangilarini kiritish
                    existing_fans.delete()
                    messages.info(request, 'Eski fanlar o\'chirilib, yangi fanlar kiritildi.')

                elif 'keep_fans' in request.POST:  # Eski fanlarni saqlash
                    messages.warning(request, 'Eski fanlar saqlanadi, faqat yangi fanlar qo\'shildi.')

            # Fanlarni kiritish yoki yangilash
            fans = []
            for name, score in zip(fan_names, fan_scores):
                try:
                    score_float = float(score)
                except ValueError:
                    messages.error(request, f"'{score}' maksimal ball sifatida noto'g'ri.")
                    return redirect('create_exam')

                fan, created = ExamFan.objects.get_or_create(
                    name=name, study_center=study_center, defaults={'ball': score_float}
                )
                if not created:
                    fan.ball = score_float  # Agar fan mavjud bo'lsa, ballni yangilash
                    fan.save()
                fans.append(fan)

            # Yangi imtihonni yaratish
            exam = Imtihonlar.objects.create(
                name=exam_name,
                study_center=study_center,
                date=exam_date_obj,
                start_time=start_time_obj,
                end_time=end_time_obj,
                exam_token=uuid.uuid4()
            )

            # Fanlarni imtihonga qo'shish
            exam.fans.set(fans)

            messages.success(request, 'Imtihon muvaffaqiyatli yaratildi!')
            return redirect('exam_detail', exam_token=exam.exam_token)  # Imtihon tafsilotlariga qaytish

        return render(request, 'imtihonlar/create_exam.html', {'title': "Imtihon yaratish", 'study_center': study_center})
    else:
        return redirect('block_error_page')



def register_for_exam(request, exam_token):
    if not request.user.is_authenticated:
        return redirect("block_error_page")

    exam = get_object_or_404(Imtihonlar, study_center=request.user.study_center, exam_token=exam_token)
    now = timezone.now()

    # Ro'yxatdan o'tish boshlanish va tugash vaqtlarini hisoblash
    registration_start = exam.date - timedelta(days=3)
    registration_end = exam.date - timedelta(hours=24)

    # Ro'yxatdan o'tish vaqtini tekshirish
    if now.date() < registration_start:
        messages.error(request, "Ro'yxatdan o'tish hali boshlanmagan!")
        return redirect("base_url")
    

    # Imtihon vaqti tugaganligini tekshirish
    if now.date() > exam.date:
        messages.error(request, "Imtihon vaqti tugagan, ro'yxatdan o'tish mumkin emas!")
        return redirect("base_url")

    if request.method == 'POST':
        # Formadan ma'lumotlarni olish
        fan_ids = request.POST.getlist('fan_choices')
        shift = request.POST.get('shift_choices')

        student = request.user

        # Ro'yxatdan o'tish holatini tekshirish
        if student in exam.students.all() or student in exam.teachers.all():
            messages.error(request, "Siz ro'yxatdan o'tib bo'lgansiz!")
            return redirect("base_url")

        # Imtihon fanlarini qo'shish
        fans = ExamFan.objects.filter(id__in=fan_ids)
        if request.user.role == 'student':
            exam.students.add(student)
        else:
            exam.teachers.add(student)

        # Fanlarni va smenani saqlash (agar kerak bo'lsa)
        # Bu qismni o'zingizning modellaringizga moslashtiring
        # Masalan:
        # student.exam_fans.set(fans)
        # if shift:
        #     student.exam_shift = shift
        # student.save()

        exam.save()

        messages.success(request, 'Siz muvaffaqiyatli ro\'yxatdan o\'tdingiz!')
        return redirect('base_url')  # O'quvchi paneliga qaytish

    else:
        shifts = [(str(i), f"Smena {i}") for i in range(1, exam.num_shifts + 1)] if hasattr(exam, 'num_shifts') and exam.num_shifts > 1 else []
        fans = ExamFan.objects.filter(study_center=exam.study_center)
        return render(request, 'imtihonlar/signup_exam.html', {
            'exam': exam,
            'fans': fans,
            'shifts': shifts
        })


def exam_list(request):
    now = timezone.now()
    today_date = now.date()
    current_time = now.time()

    # 7 kun ichida bo'ladigan imtihonlarni olish
    seven_days_later = today_date + timedelta(days=7)
    upcoming_exams = Imtihonlar.objects.filter(
        date__gte=today_date,
        date__lte=seven_days_later,
        study_center=request.user.study_center
    ).filter(
        Q(date__gt=today_date) |
        (Q(date=today_date) & Q(end_time__gt=current_time))
    ).order_by('date', 'start_time')

    # Hozirda davom etayotgan imtihonlarni olish
    ongoing_exams = Imtihonlar.objects.filter(
        date=today_date,
        study_center=request.user.study_center
    )

    # Tugagan imtihonlarni olish
    completed_exams = Imtihonlar.objects.filter(
        Q(date__lt=today_date) |
        (Q(date=today_date) & Q(end_time__lte=current_time)),
        study_center=request.user.study_center
    ).order_by('-date', '-end_time')

    context = {
        'upcoming_exams': upcoming_exams,
        'ongoing_exams': upcoming_exams,
        'completed_exams': completed_exams,
    }
    return render(request, 'imtihonlar/exam_list.html', context)


@login_required
def exam_detail(request, exam_token):
    exam = get_object_or_404(Imtihonlar, exam_token=exam_token, study_center=request.user.study_center)

    # Qatnashuvchi o'quvchilar
    students = exam.students.all().order_by('first_name', 'last_name')

    # Imtihon oluvchi o'qituvchilar
    teachers = exam.teachers.all().order_by('first_name', 'last_name')

    # Eng yuqori ball olgan o'quvchilar (top 10)
    top_students = StudentResult.objects.filter(exam=exam).order_by('-results')[:10]

    context = {
        'exam': exam,
        'students': students,
        'teachers': teachers,
        'top_students': top_students,
    }

    return render(request, 'imtihonlar/exam_detail.html', context)



def add_student_result(request):
    if request.method == 'POST':
        group_id = request.POST.get('group')
        student_id = request.POST.get('student')
        checker_id = request.POST.get('checker_hidden')
        exam_id = request.POST.get('exam')

        if not group_id or not student_id or not checker_id or not exam_id:
            return JsonResponse({'error': "Guruh, o'quvchi, o'qituvchi yoki imtihon tanlanmagan."}, status=400)

        try:
            group = Group.objects.get(id=group_id, study_center=request.user.study_center)
            student = Account.objects.get(id=student_id, study_center=request.user.study_center)
            checker = Account.objects.get(id=checker_id)
            exam = Imtihonlar.objects.get(id=exam_id, study_center= request.user.study_center)

            # O'quvchining fanlari bo'yicha natijalarni olish
            results = {}
            for fan in student.fanlar.all():
                result = request.POST.get(f'subject_{fan.id}')  # O'quvchining fan IDsi bilan nomi
                if result is not None:
                    results[fan.name] = float(result)
                    result = float(result)
                    student.month_score += result
                    student.total_score += result
                    student.save()
                    # Natijalarni float ga aylantirish

            # Natijani saqlash
            student_result = StudentResult.objects.create(
                student=student,
                checker=checker,
                exam=exam,
                results=results
            )
            student_result.save()

            messages.success(request, "Natija muvaffiqiyatli saqlandi!")
            return redirect('exam_detail', exam_token=exam.exam_token)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Agar GET bo'lsa
    groups = Group.objects.filter(study_center=request.user.study_center)
    exams = Imtihonlar.objects.filter(study_center=request.user.study_center)

    return render(request, 'imtihonlar/add_result.html', {
        'groups': groups,
        'exams': exams,
    })

# O'quvchining fanlarini qaytarish uchun yangi view


@login_required
def get_students_by_group(request, group_id):
    if request.user.role in ['director', 'teacher']:
        if request.method == 'GET':
            students = Account.objects.filter(groups__id=group_id, study_center=request.user.study_center)
            student_data = [{'id': student.id, 'first_name': student.first_name, 'last_name': student.last_name} for student in students]
            return JsonResponse({'students': student_data})
    else:
        return JsonResponse({'error': "Sizga kirish mumkin emas!"})
@login_required
def get_student_subjects(request, student_id):
    if request.user.role in ['director', 'teacher']:
        if request.method == 'GET':
            student = Account.objects.get(id=student_id)
            subjects = student.fanlar.all()
            subject_data = [{'id': subject.id, 'name': subject.name} for subject in subjects]
            return JsonResponse({'fanlar': subject_data})
    else:
            return JsonResponse({'error': "Sizga kirish mumkin emas!"})