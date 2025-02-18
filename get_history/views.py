from django.shortcuts import render, redirect
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator  # Paginator import qilamiz

@login_required
def models_history_view(request):
    histories = Account.history.all().order_by('-history_date')
    
    # Pagination qo'shamiz
    paginator = Paginator(histories, 10)  # Har bir sahifada 10 ta element ko'rsatiladi
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'history/all_models.html', {'page_obj': page_obj, 'user_role': request.user.role})

@login_required
def teachers_history(request):
    if request.user.is_authenticated and request.user.role == 'director':
        
        teachers = request.user.study_center.teachers.all()
        teacher_histories = []
        for teacher in teachers:
            teacher_histories.extend(teacher.history.all())

        # Pagination qo'shamiz
        paginator = Paginator(teacher_histories, 10)  # Har bir sahifada 10 ta element ko'rsatiladi
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        data = {
            'page_obj': page_obj
        }
        return render(request, 'history/history.html', data)
    else:
        return redirect('/')

@login_required
def student_history(request):
    if request.user.is_authenticated and request.user.role == 'director':
        students = request.user.study_center.students.all()
        student_histories = []
        for student in students:
            student_histories.extend(student.history.all())

        # Pagination qo'shamiz
        paginator = Paginator(student_histories, 10)  # Har bir sahifada 10 ta element ko'rsatiladi
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        data = {
            'page_obj': page_obj
        }
        
        return render(request, 'history/history.html', data)
    else:
        return redirect('/')
