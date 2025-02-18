from django.contrib import admin
from .models import StudentResult, Imtihonlar, ExamFan
from django.contrib.admin import ModelAdmin
# Register your models here.
# admin.site.register([StudentResult, ExamFan, Imtihonlar])

@admin.register(ExamFan)
class ExamFanAdmin(ModelAdmin):
    list_display = ('id', 'name', 'study_center', 'ball')
    list_filter = ('study_center', )
    list_display_links = ('id', 'name', )
    search_fields = ('id', 'name', )

@admin.register(Imtihonlar)
class ImtihonAdmin(ModelAdmin):
    list_display = ('id', 'name', 'study_center', 'date', 'start_time', 'end_time')
    list_filter = ('study_center', )
    list_display_links = ('id', 'name', )
    search_fields = ('id', 'name', )

@admin.register(StudentResult)
class StudentResultAdmin(ModelAdmin):
    list_display = ('id', 'student_full_name', 'checker_full_name', 'exam_name')
    list_filter = ('exam__name', )
    list_display_links = ('id', 'student_full_name')
    search_fields = ('student__first_name', 'student__last_name', 'checker__first_name', 'checker__last_name')

    def student_full_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"
    student_full_name.short_description = 'Student Name'

    def checker_full_name(self, obj):
        return f"{obj.checker.first_name} {obj.checker.last_name}"
    checker_full_name.short_description = 'Checker Name'

    def exam_name(self, obj):
        return obj.exam.name
    exam_name.short_description = 'Exam'