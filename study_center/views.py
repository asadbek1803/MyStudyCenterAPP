import json
from django.utils import timezone
from .models import Payments
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .models import StudyCenter, Fanlar, Group, LessonsTable, Days, LessonSchedule, Attendance, AttendanceRecord
from accounts.models import Account
from django.db import IntegrityError
from datetime import datetime, timedelta
from accounts.models import NotifactionMessage
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt


# >>>>>>>>>>>>>>>>>>>>>>> Add Study Center <<<<<<<<<<<<<<<<< 
@login_required
def add_study_center(request):
    if request.user.role != 'director':
        return redirect('block_error_page')
    if request.user.study_center:
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        admin = request.POST.get('admin')
        logo = request.FILES.get('logo')
        description = request.POST.get('description')
        address = request.POST.get('address')

        if name and admin and description and address and logo:
            study_center = StudyCenter.objects.create(
                name=name,
                admin=admin,
                logo=logo,
                description=description,
                address=address,
            )
            request.user.study_center = study_center
            request.user.save()
            return redirect(reverse('dashboard'))
        else:
            return render(request, 'dashboard/add_study_center.html', {'error': 'Hamma qatorlarni to\'ldiring!'})

    return render(request, 'dashboard/add_study_center.html')

#  >>>>>>>>>>>>>>>>>>>>>> Subjects view <<<<<<<<<<<<<<<<<<<<<

@login_required
def fanlar(request):
    if request.user.role == 'student':
        return redirect('/')
    
    if not request.user.study_center:
        messages.error(request, "O'quv markaz topilmadi.")
        return redirect('/')

    fanlar = Fanlar.objects.filter(teacher__study_center=request.user.study_center).select_related('teacher')
    data = {'fanlar': fanlar}
    return render(request, 'dashboard/fanlar.html', data)

@login_required
def delete_fan(request, fan_nomi):
    if request.user.role == 'director':
        fan = get_object_or_404(Fanlar, name=fan_nomi)
        fan.delete()
        return redirect('fanlar')
    return redirect(reverse('block_error_page'))



@login_required
def add_fan(request):
    if request.user.role == 'director':
        if request.method == 'POST':
            name = request.POST.get('name')
            teacher_id = request.POST.get('teacher')

            if not name or not teacher_id:
                messages.error(request, "Hamma maydonlarni to'ldirish shart!")
                return redirect('add_fan')

            teacher = get_object_or_404(Account, id=teacher_id)

            Fanlar.objects.create(name=name, teacher=teacher, study_center = request.user.study_center)
            messages.success(request, "Fan muvaffaqiyatli saqlandi!")
            return redirect('fanlar')

        study_center = request.user.study_center
        if study_center:
            teachers = study_center.teachers.filter(is_active=True)
            data = {'teachers': teachers}
            return render(request, 'dashboard/add_fan.html', data)
        else:
            messages.error(request, "O'quv markazi mavjud emas!")
            return render(request, 'dashboard/add_fan.html', {'error': 'Study Center not found for this user.'})

    return redirect(reverse('block_error_page'))


@login_required
def edit_fan(request, fan_id):
    if request.user.role == 'director':
        fan = get_object_or_404(Fanlar, id=fan_id)
        
        if request.method == 'POST':
            name = request.POST.get('name')
            teacher_id = request.POST.get('teacher')

            if not name or not teacher_id:
                messages.error(request, "Hamma maydonlarni to'ldirish shart!")
                return redirect('edit_fan', fan_id=fan_id)

            teacher = get_object_or_404(Account, id=teacher_id)
            fan.name = name
            fan.teacher = teacher
            fan.save()

            messages.success(request, "Fan muvaffaqiyatli saqlandi!")
            return redirect('fanlar')

        study_center = request.user.study_center
        if study_center:
            teachers = study_center.teachers.filter(is_active=True)
            data = {'teachers': teachers, 'fan': fan}
            return render(request, 'dashboard/edit/edit_fan.html', data)
        messages.error(request, "O'quv markazi mavjud emas!")
        return render(request, 'dashboard/edit/edit_fan.html', {'error': 'Study Center not found for this user.'})
    else:
        return redirect(reverse('block_error_page'))
   
        


# >>>>>>>>>>>>>>>>>>>>>>>>  Gropus view <<<<<<<<<<<<<<<<<<<<<<

@login_required
def guruhlar(request):
    if request.user.role == 'director' or request.user.role == 'teacher':
        study_center = request.user.study_center
        groups = Group.objects.filter(study_center=study_center)
        data = {'groups': groups}
        return render(request, 'dashboard/guruhlar.html', data)
    return redirect('/')

@login_required
def delete_guruh(request, guruh_nomi):
    if request.user.role == 'director':
        guruh = get_object_or_404(Group, name=guruh_nomi)
        guruh.delete()
        return redirect('guruhlar')
    return redirect(reverse('block_error_page'))

@login_required
def add_guruh(request):
    if request.user.role == 'director':
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            logo = request.FILES.get('logo')
            teacher_id = request.POST.get('teacher')
            fan_id = request.POST.get('fan')
            study_center = request.user.study_center

            if not name or not teacher_id or not fan_id:
                messages.error(request, "Ba'zi qatorlarni to'ldirish shart!")
                return redirect('add_guruh')

            teacher = get_object_or_404(Account, id=teacher_id)
            fan = get_object_or_404(Fanlar, id=fan_id)

            guruh = Group.objects.create(
                name=name,
                description=description,
                group_logo=logo,
                study_center=study_center
            )

            guruh.fan.add(fan)
            guruh.teachers.add(teacher)
            messages.success(request, 'Guruh muvaffaqiyatli saqlandi!')
            return redirect('guruhlar')

        study_center = request.user.study_center
        if study_center:
            teachers = study_center.teachers.all()
            fanlar = Fanlar.objects.filter(teacher__study_center=study_center)

            data = {
                'teachers': teachers,
                'fanlar': fanlar
            }
            return render(request, 'dashboard/add_guruh.html', data)

    return redirect(reverse('block_error_page'))


@login_required
def single_guruh(request, slug):
    if request.user.role == 'director' or request.user.role == 'teacher':
        guruh = get_object_or_404(Group, slug=slug)
        
        students = guruh.students.all()
        student_fanlar = {student: student.fanlar.all() for student in students}

        data = {
            'guruh': guruh,
            'teachers': guruh.teachers.all(),
            'total_students': guruh.students.count(),
            'students': students,
            'student_fanlar': student_fanlar, 
        }
        
        return render(request, 'dashboard/single_guruh.html', data)

    return redirect(reverse('block_error_page'))


# >>>>>>>>>>>>>>>>>>> Teachers view <<<<<<<<<<<<<<<<<<<<<<


@login_required
def teachers_view(request):
    if request.user.role in ['director', 'teacher']:
        study_center = request.user.study_center
        status_filter = request.GET.get('status')
        
        # Filtrlashni bitta queryda qilish
        
        if status_filter == 'True':
            working = study_center.teachers.filter(is_active=True)
            paginator = Paginator(working, 10)
        elif status_filter == 'False':
            unworking = study_center.teachers.filter(is_active=False)
            paginator = Paginator(unworking, 10)
        else:
            all = study_center.teachers.all()
            paginator = Paginator(all, 10)
        
        
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'dashboard/teachers.html', {
            'page_obj': page_obj,
            'status_filter': status_filter,
            
        })
    
    return redirect('/')


@login_required
def delete_teacher(request, username):
    if request.user.role == 'director':
        teacher = get_object_or_404(Account, username=username, role='teacher', study_center = request.user.study_center)
        teacher.delete()
        messages.success(request, "O'qituvchi muvaffaqiyatli o'chirildi!")
        return redirect('teachers')
    
    return redirect('login')


@login_required
def delete_student(request, username):
    if request.user.role in ['director', 'teacher']:
        teacher = get_object_or_404(Account, username=username, role='student', study_center=request.user.study_center)
        teacher.delete()
        messages.success(request, "O'quvchi muvaffaqiyatli o'chirildi!")
        return redirect('students')

    return redirect('login')


@login_required
def download_credits(request, username):
    if request.user.role == 'director':
        teacher = get_object_or_404(Account, username=username, role='teacher', study_center = request.user.study_center)
        
        # Parollarni ochiq shaklda yubormaslik uchun yangi tizim kerak
        content = (
            f'Username: {teacher.username}\n'
            f'Email: {teacher.email}\n'
            f'Phone: {teacher.phone}\n'
        )
        
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{teacher.first_name}_{teacher.last_name}_credentials.txt"'
        return response
    
    return redirect('/')


@login_required
def add_teacher(request):
    if request.user.role != 'director':
        return redirect('login')

    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            logo = request.FILES.get('logo')
            address = request.POST.get('address')
            description = request.POST.get('description')
            fan_id = request.POST.get('fan')
            password = request.POST.get('password')
            confirm_password = request.POST.get('password2')

            # Parollar mos kelishini tekshirish
            if password != confirm_password:
                raise ValueError('Parollar mos kelmadi.')

            # O'qituvchini yaratish
            fan = Fanlar.objects.get(id=fan_id) if fan_id else None
            new_teacher = Account.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                profile_image=logo,
                phone=phone,
                address=address,
                description=description,
                study_center=request.user.study_center,
                role='teacher'
            )

            if fan:
                new_teacher.fanlar.add(fan)
            
            # Study Centerga o'qituvchini qo'shish
            request.user.study_center.teachers.add(new_teacher)
            messages.success(request, 'O\'qituvchi muvaffaqiyatli yaratildi!')
            return redirect('teachers')

        except (IntegrityError, ObjectDoesNotExist, ValueError) as e:
            messages.error(request, f'Xato: {e}')
            return redirect('add_teacher')

    fanlar = Fanlar.objects.filter(teacher__study_center=request.user.study_center)
    return render(request, 'dashboard/add_teacher.html', {'fanlar': fanlar})


@login_required
def edit_teacher(request, username):
    if request.user.role != 'director':
        return redirect('/')

    teacher = get_object_or_404(Account, username=username, role='teacher', study_center = request.user.study_center)

    if request.method == 'POST':
        try:
            teacher.username = request.POST.get('username')
            teacher.first_name = request.POST.get('first_name')
            teacher.last_name = request.POST.get('last_name')
            teacher.email = request.POST.get('email')
            teacher.phone = request.POST.get('phone')
            teacher.address = request.POST.get('address')
            teacher.description = request.POST.get('description')
            teacher.is_active = request.POST.get('is_active', teacher.is_active)
            
            logo = request.FILES.get('logo')
            if logo:
                teacher.profile_image = logo

            fan_id = request.POST.get('fan')
            if fan_id:
                fan = Fanlar.objects.get(id=fan_id)
                teacher.fan = fan

            password = request.POST.get('password')
            confirm_password = request.POST.get('password2')
            if password and password == confirm_password:
                teacher.set_password(password)
            elif password != confirm_password:
                raise ValueError('Parollar mos kelmadi.')
            
            teacher.save()
            messages.success(request, 'O\'qituvchi muvaffaqiyatli saqlandi!')
            return redirect('teachers')

        except (ObjectDoesNotExist, ValueError) as e:
            messages.error(request, f'Xato: {e}')
            return redirect('edit_teacher', username=username)

    fanlar = Fanlar.objects.filter(teacher__study_center=request.user.study_center)
    return render(request, 'dashboard/edit/edit_teacher.html', {
        'teacher': teacher,
        'fanlar': fanlar
    })


@login_required
def leave_teacher(request, username):
    if request.user.role in ['director', 'teacher']:
        teacher = get_object_or_404(Account, username=username, role='teacher', study_center = request.user.study_center)
        
        groups = Group.objects.filter(teachers=teacher)
        if groups.exists():
            for group in groups:
                group.teachers.remove(teacher)
        
        teacher.is_active = False
        teacher.save()
        messages.success(request, f"{teacher.first_name} {teacher.last_name} o'qituvchi muvaffaqiyatli o'chirildi!")
        return redirect('teachers')

    return redirect('/')
# >>>>>>>>>>>>>>>>>>>>>>>>>>> Students <<<<<<<<<<<<<<<<<<<<<<<<<<<

@login_required
def add_student(request):
    if request.user.role not in ['director', 'teacher']:
        return redirect(reverse('block_error_page'))

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        phone_home = request.POST.get('phone_home')
        logo = request.FILES.get('profile_image')
        address = request.POST.get('address')
        description = request.POST.get('description')
        is_grand = request.POST.get('is_grand') == 'on'
        group_id = request.POST.get('group_id')
        fanlar_ids = request.POST.getlist('fanlar')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password2')

        if password != confirm_password:
            messages.error(request, 'Parollar mos kelmadi.')
            return redirect('add_student')

        try:
            # Yangi talaba yaratish
            student = Account.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                phone_home=phone_home,
                address=address,
                description=description,
                is_grand=is_grand,
                profile_image=logo,
                study_center=request.user.study_center,
                role='student'
            )

            if group_id:
                group = Group.objects.get(id=group_id)
                group.students.add(student)
                student.groups.add(group)

            fanlar = Fanlar.objects.filter(id__in=fanlar_ids)
            student.fanlar.set(fanlar)

            study_center = request.user.study_center
            study_center.students.add(student)

            # Foydalanuvchiga `user_id` ni ko'rsatish
            messages.info(request, "UserID ni saqlab qo'ying dasturga kirilyotganda ishlatiladi. Aks holda kirib bo'lmaydi!")
            messages.success(request, f'Talaba muvaffaqiyatli saqlandi! User ID: {student.user_id}')
            return redirect('students')
        except Exception as e:
            messages.error(request, f'Xatolik yuz berdi: {str(e)}')
            return redirect('add_student')

    groups = Group.objects.filter(study_center=request.user.study_center)
    fanlar = Fanlar.objects.filter(teacher__study_center=request.user.study_center)

    data = {
        'groups': groups,
        'fanlar': fanlar,
        'user_id': "Ro'yxatdan o'tish tugagandan so'ng paydo bo'ladi!"
    }
    return render(request, 'dashboard/add_student.html', data)



@login_required
def leave_student(request, student_username):
    if request.user.role in ['director', 'teacher']:
        student = get_object_or_404(Account, username=student_username, role='student', study_center__id=request.user.study_center.id)

        # Talabani barcha guruhlardan o'chirish
        groups = student.groups.all()
        for group in groups:
            group.students.remove(student)
            group.leave_student_counter += 1
            group.save()

        # Talabani deaktivatsiya qilish
        student.is_leave = True
        student.is_active = False
        student.save()

        messages.success(request, f"{student.first_name} {student.last_name} o'quvchi o'chirildi!")
        return redirect('students')
    
    return redirect('/')


@login_required
def get_students(request):
    if request.user.role in ['director', 'teacher']:
        study_center = request.user.study_center
        status_filter = request.GET.get('status')
        group_filter = request.GET.get('guruh')
        groups = Group.objects.filter(study_center=study_center).all()

        # Talabalarni filtrlash va tartiblash
        students = study_center.students.all()

        if status_filter == 'True':
            students = students.filter(is_active=True)
        elif status_filter == 'False':
            students = students.filter(is_active=False)

        if group_filter and group_filter != 'all':
            students = students.filter(groups__slug=group_filter)

        students = students.order_by('-last_name')
        paginator = Paginator(students, 10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'dashboard/students.html', {
            'page_obj': page_obj,
            'status_filter': status_filter,
            'group_filter': group_filter,
            'groups': groups,
        })
    
    return redirect('/')


@login_required
def edit_student(request, username):
    if request.user.role not in ['director', 'teacher']:
        return redirect(reverse('block_error_page'))

    student = get_object_or_404(Account, username=username, role='student')

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        phone_home = request.POST.get('phone_home')
        logo = request.FILES.get('logo')
        address = request.POST.get('address')
        description = request.POST.get('description')
        is_grand = request.POST.get('is_grand') == 'True'
        is_active = request.POST.get('is_active') == 'True'
        password = request.POST.get('password')
        confirm_password = request.POST.get('password2')
        fanlar_ids = request.POST.getlist('fanlar')
        guruhlar_ids = request.POST.getlist('guruhlar')

        # Parolni yangilash qismini alohida tekshiramiz
        if password:
            if password != confirm_password:
                messages.error(request, 'Parollar mos kelmadi.')
                return redirect('edit_student', username=username)
            else:
                # Parol to'g'ri kiritilgan bo'lsa, uni yangilaymiz
                student.set_password(password)

        # Boshqa ma'lumotlarni yangilash
        student.username = username
        student.first_name = first_name
        student.last_name = last_name
        student.email = email
        student.phone = phone
        student.phone_home = phone_home
        student.address = address
        student.description = description
        student.is_grand = is_grand
        student.is_active = is_active

        if logo:
            student.profile_image = logo

        # Fanlar va guruhlarni yangilash
        selected_fanlar = Fanlar.objects.filter(id__in=fanlar_ids)
        student.fanlar.set(selected_fanlar)

        # Guruhlarni yangilash
        old_groups = set(student.groups.all())
        new_groups = set(Group.objects.filter(id__in=guruhlar_ids))

        # O'quvchini yangi guruhlarga qo'shish
        for group in new_groups - old_groups:
            group.students.add(student)

        # O'quvchini eski guruhlardan olib tashlash
        for group in old_groups - new_groups:
            group.students.remove(student)

        student.groups.set(new_groups)

        student.is_leave = is_active
        student.save()
        messages.success(request, "O'quvchi muvaffaqiyatli saqlandi!")
        return redirect('students')

    # GET request uchun
    fanlar = Fanlar.objects.filter(teacher__study_center=request.user.study_center)
    groups = Group.objects.filter(study_center=request.user.study_center)

    data = {
        'student': student,
        'fanlar': fanlar,
        'groups': groups
    }
    return render(request, 'dashboard/edit/edit_student.html', data)

@login_required
def lessons_list(request):
    if request.user.role == 'director' or request.user.role == 'teacher':
        study_center_id = request.user.study_center.id
        lessons = LessonsTable.objects.filter(study_center__id=study_center_id).all()

        data = {
            'lessons': lessons
        }
        return render(request, 'dashboard/lessons.html', data)
    else:
        return redirect('/')


@login_required
def check_payments(request):
    if request.user.role == 'director' or request.user.role == 'teacher':
        my_study_center = request.user.study_center
        now_date = datetime.now().date()
        not_payed = []
        payed = []
        grand_objs = []
        never_pay_objs = []
        payed_counter = 0
        not_payed_counter = 0
        never_payed = 0
        grand = 0
        students = my_study_center.students.all()
        status_filter = request.GET.get('status')

        # Talabalarni filtrlash
        for student in students:
            if student.is_grand:
                grand += 1
                student_groups = student.groups.all()
                grand_objs.append({'student': student, 'groups': student_groups})
                continue

            elif student.last_payment_date is None:
                never_payed += 1
                student_groups = student.groups.all()
                never_pay_objs.append({'student': student, 'groups': student_groups})
                continue

            last_payment_date = student.last_payment_date.date() if isinstance(student.last_payment_date, datetime) else student.last_payment_date
            days_since_last_payment = (now_date - last_payment_date).days

            if days_since_last_payment > 30:
                not_payed_counter += 1
                student_groups = student.groups.all()
                not_payed.append({'student': student, 'groups': student_groups})
            else:
                student_groups = student.groups.all()
                payed.append({'student': student, 'groups': student_groups})
                payed_counter += 1

        # Sahifalashni qo'shish
        if status_filter == 'not_payed':
            paginator = Paginator(not_payed, 10)
        elif status_filter == '' or status_filter == ' ':
            paginator = Paginator(not_payed + payed + grand_objs + never_pay_objs, 10)
        elif status_filter == 'payed':
            paginator = Paginator(payed, 10)
        elif status_filter == 'grand':
            paginator = Paginator(grand_objs, 10)
        elif status_filter == 'never_pay':
            paginator = Paginator(never_pay_objs, 10)
        else:
            paginator = Paginator(not_payed + payed + grand_objs + never_pay_objs, 10)
        
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        data = {
            'title': 'To\'lovlarni tekshirish',
            'page_obj': page_obj,
            'not_payed_counter': not_payed_counter,
            'payed_counter': payed_counter,
            'grand_counter': grand,
            'never_payed_counter': never_payed,
            'total_students_counter': students.count(),
            'status_filter': status_filter
        }
        return render(request, "dashboard/payments.html", data)

    else:
        return redirect('/')
    
    
@csrf_exempt
@login_required
def send_payment_reminder(request):
    if request.user.role == 'director' or request.user.role == 'teacher':
        if request.method == "POST":
            data = json.loads(request.body)
            student_id = data.get('student_id')
            message_text = data.get('message', 'Siz to\'lovni amalga oshirishingiz kerak.')
            
            try:
                student = Account.objects.get(id=student_id)
                sender = request.user  # Sender - xabar yuborayotgan foydalanuvchi

                # Yangi xabarni yaratish
                notification = NotifactionMessage.objects.create(message=message_text, sender=sender)
                notification.receiver.add(student)  # Talabani qabul qiluvchilar ro'yxatiga qo'shish

                # Xabar muvaffaqiyatli yaratildi
                return JsonResponse({"success": True})
            except Account.DoesNotExist:
                return JsonResponse({"success": False, "error": "Talaba topilmadi."})
        else:
            return JsonResponse({"success": False, "error": "Noto'g'ri so'rov usuli."})
    else:
        return redirect(reverse('block_error_page'))
    





@login_required
def create_payment(request, user_id):
    if request.user.role in ['director', 'teacher']:
        student = get_object_or_404(Account, user_id=user_id)
        if student.is_grand:
            messages.error(request, f"{student.first_name} {student.last_name} uchun to'lov amalga oshirilmaydi, chunki ushbu o'quvchi to'lovdan ozod qilingan.")
            return redirect('students')
        now = timezone.now()
        center = request.user.study_center # Barcha fanlarni olamiz
        subjects = student.fanlar.all()

        if request.method == "POST":
            subject_id = request.POST.get('subject')
            subject = get_object_or_404(Fanlar, id=subject_id)
            amount = request.POST.get('amount')
            payment_type = request.POST.get('type')

            # O'tgan oylik to'lovni tekshirish
            last_payment = Payments.objects.filter(student=student, subject=subject).order_by('-created_date').first()

            if last_payment and last_payment.created_date.month == now.month:
                messages.error(request, f"Siz {subject.name} fani uchun hozirgi oy uchun to'lovni allaqachon amalga oshirdingiz.")
                return redirect('students')

            if last_payment and (now - last_payment.created_date).days > 30:
                messages.warning(request, f"Siz {subject.name} fani uchun o'tgan oy uchun to'lovni amalga oshirmadingiz. Iltimos, oldingi oy uchun to'lov qiling.")
                return redirect('students')

            # To'lovni yaratish
            Payments.objects.create(student=student, study_center=request.user.study_center,  teacher=request.user, subject=subject, amount=amount, type=payment_type)
            student.last_payment_date = now
            student.save()

            messages.success(request, f"{subject.name} fani uchun to'lov muvaffaqiyatli amalga oshirildi.")
            return redirect('payment_summary', student.user_id)

        return render(request, 'payments/create_payment.html', {'student': student, 'subjects': subjects})
    else:
        return redirect("block_error_page")

@login_required
def payment_summary(request, user_id):
    student = get_object_or_404(Account, user_id = user_id)
    payments = Payments.objects.filter(student=student)
    
    total_amount = 0  # Umumiy to'lov miqdorini boshlang'ich 0 deb belgilaymiz

    for payment in payments:
        try:
            total_amount += float(payment.amount)
        except ValueError:
            messages.error(request, f"To'lov {payment.id} uchun noto'g'ri formatdagi miqdor: {payment.amount}")
    
    return render(request, 'payments/payments-summary.html', {
        'payments': payments,
        'student': student,
        'total_amount': total_amount
    })
    



# Yangi dars yaratish (Create)
def lesson_create(request):
    if request.user.role in ['director', 'teacher']:
        if request.method == 'POST':
            group = get_object_or_404(Group, pk=request.POST.get('group'))
            study_center = request.user.study_center

            lesson = LessonsTable.objects.create(group=group, study_center=study_center)

            days = request.POST.getlist('days')
            times = request.POST.getlist('times')

            for day, time in zip(days, times):
                LessonSchedule.objects.create(lesson=lesson, day=day, time=time)


            messages.success(request, "Dars jadvali muvaffiqiyatli yaratildi!")
            return redirect('lessons')

        groups = Group.objects.all()
        study_centers = request.user.study_center
        return render(request, 'dashboard/add_lesson.html', {'groups': groups, 'study_centers': study_centers})
    else:
        return redirect("block_error_page")
# Darsni yangilash (Update)

@login_required
def lessons_update(request, pk):
    if request.user.role in ['teacher', 'director']:
        
        lesson = get_object_or_404(LessonsTable, id=pk)

        if request.method == 'POST':
            # Guruhni yangilash uchun POST request
            group_id = request.POST.get('group')
            group = get_object_or_404(Group, id=group_id)

            # O'qituvchilarni yangilash
            teacher_ids = request.POST.getlist('teachers')
            teachers = Account.objects.filter(id__in=teacher_ids)
            
            # LessonSchedule yangilash
            days = request.POST.getlist('days')
            times = request.POST.getlist('times')

            # O‘quv markaz ma'lumotlarini yangilash
            lesson.group = group
            lesson.save()

            lesson.schedules.all().delete()  # Eski jadvalni o‘chirish

            for day, time in zip(days, times):
                LessonSchedule.objects.create(lesson=lesson, day=day, time=time)
            
            lesson.group.teachers.set(teachers)

            messages.success(request, "Dars muvaffaqiyatli yangilandi!")
            return redirect('lessons')

        groups = Group.objects.filter(study_center=lesson.study_center)
        teachers = Account.objects.filter(study_center=lesson.study_center)

        context = {
            'title': 'Darsni yangilash',
            'lesson': lesson,
            'groups': groups,
            'teachers': teachers,
            'days': LessonSchedule.DAYS
        }
        return render(request, 'dashboard/edit/edit_lesson.html', context)
    
    else:
        return redirect('block_error_page')

# Darsni o'chirish (Delete)

@login_required
def lessons_delete(request, pk):
    if request.user.role in ['teacher', 'director']:
        lesson = get_object_or_404(LessonsTable, pk=pk)
        lesson.delete()
        return redirect('lessons')
    else:
        return redirect('block_error_page')



def get_today_day_in_uzbek():
    days_in_uzbek = {
        'Monday': 'Duyshanba',
        'Tuesday': 'Seshanba',
        'Wednesday': 'Chorshanba',
        'Thursday': 'Payshanba',
        'Friday': 'Juma',
        'Saturday': 'Shanba',
        'Sunday': 'Yakshanba'
    }

    now_day = timezone.now().strftime('%A')
    return days_in_uzbek.get(now_day, 'Noma\'lum kun')

@login_required
def today_lessons_view(request):
    if request.user.role in ['teacher', 'director']:
        # Bugungi kunni o'zbek tilida olish
        today = get_today_day_in_uzbek()


        # Bugungi dars jadvalini olish
        lesson_schedules = LessonSchedule.objects.filter(day=today)

        # Bugungi darslari bo'lgan guruhlarni olish
        groups = Group.objects.filter(lessonstable__schedules__in=lesson_schedules).distinct()

        # Agar bugungi darslari bo'lgan guruhlar topilmasa
        if not groups:
            messages.error(request, 'Bugungi darslari mavjud guruhlar topilmadi.')

        context = {
            'title': 'Bugungi darslari mavjud guruhlar uchun davomat',
            'groups': groups,
            'today': today,
        }
        return render(request, 'attendance/groups_list.html', context)
    else:
        return redirect("block_error_page")


@login_required
def take_attendance(request, group_slug):
    if request.user.role in ['director', 'teacher']:

        group = get_object_or_404(Group, slug=group_slug)

        today = timezone.now().date()
        current_time = timezone.now().time()

        # Bugungi kun uchun dars jadvalini tekshirish
        lessons_table = get_object_or_404(LessonsTable, group=group)
        today_schedule = LessonSchedule.objects.filter(
            lesson=lessons_table
        ).order_by('-time').first()

        # Agar bugungi jadval topilmasa, xatolik chiqarish
        if not today_schedule:
            messages.error(request, "Bugun ushbu guruh uchun dars jadvali topilmadi.")
            return redirect('today_lessons_view')

        # Davomat yozuvini yaratish yoki olish
        attendance_record, created = AttendanceRecord.objects.get_or_create(
            group=group,
            date=today
        )

        if request.method == 'POST':
            if attendance_record.is_completed:
                messages.error(request, "Bugungi davomat allaqachon yakunlangan.")
                return redirect("today_lessons_view")
                # return JsonResponse({'error': 'Bugungi davomat allaqachon yakunlangan.'}, status=400)

            for student_id, status in request.POST.items():
                if student_id.startswith('student_'):
                    student_id = student_id.split('_')[1]
                    student = get_object_or_404(Account, id=student_id)
                    try:
                        attendance = Attendance.objects.get(
                            student=student,
                            lesson_schedule=today_schedule,
                            date=today
                        )
                        if not attendance.locked:
                            attendance.is_present = status == 'present'
                            attendance.save()
                    except Attendance.DoesNotExist:
                        Attendance.objects.create(
                            student=student,
                            lesson_schedule=today_schedule,
                            date=today,
                            study_center = request.user.study_center,
                            is_present=status == 'present'
                        )

            attendance_record.is_completed = True
            attendance_record.study_center = request.user.study_center
            attendance_record.save()
            messages.success(request, "Davomat muvaffiqiyatli saqlandi!")
            return redirect("today_lessons_view")

        students = group.students.all()
        attendances = Attendance.objects.filter(
            lesson_schedule=today_schedule,
            date=today
        )
        attendance_dict = {a.student_id: a.is_present for a in attendances}

        context = {
            "title": f"{group.name} uchun davomat olish",
            'group': group,
            'students': students,
            'attendances': attendance_dict,
            'is_completed': attendance_record.is_completed,
            'date': today,
            'lesson_schedule': today_schedule
        }
        return render(request, 'attendance/take-attendance.html', context)
    else:
        return redirect("block_error_page")

@login_required
def attendance_select_view(request):
    if request.user.role in ['director', 'teacher']:
        groups = Group.objects.filter(study_center = request.user.study_center)

        selected_group = request.GET.get('group')
        selected_date = request.GET.get('date')
        attendances = None
        attendance_dates = None
        # group = get_object_or_404(Group, id=selected_group)
        if selected_group:
            group = get_object_or_404(Group, id=selected_group)
            # Ushbu guruhga oid olingan davomat sanalarini olish
            attendance_dates = AttendanceRecord.objects.filter(group=group).values_list('date', flat=True)

            if selected_date:
                # Sanani YYYY-MM-DD formatiga o'tkazish
                try:
                    formatted_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
                    # Tanlangan guruh va sana bo'yicha davomatlarni olish
                    attendances = Attendance.objects.filter(
                        lesson_schedule__lesson__group=group,
                        date=formatted_date
                    )
                except ValueError:
                    attendances = None

        context = {
            'groups': groups,
            'attendance_dates': attendance_dates,
            'attendances': attendances,
            'selected_group': selected_group,
            'selected_date': selected_date,
        }
        return render(request, 'attendance/attendance_select.html', context)
    else:
        return redirect("block_error_page")
@login_required
def all_month_score_zero(request):
    day = datetime.now().day
    if request.user.role in ['director', 'teacher']:
        if day == 1:
            students = Account.objects.filter(role='student', study_center=request.user.study_center)
            counter = 0
            for student in students:
                student.month_score = 0
                counter += 1
                student.save()

            messages.success(request, f"Barcha o'quvchilarning oylik ballari 0 ga tushirildi! Baza yangilandi {counter} o'quvchiga.")
            return redirect("students")
        else:
            messages.error(request, "Bugun oyning birinchi kuni emas!")
            return redirect("students")
    else:
        return redirect("block_error_page")
