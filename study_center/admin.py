from django.contrib import admin
from .models import StudyCenter, Group, LessonSchedule, AttendanceRecord, Fanlar, LessonsTable, Days, Payments, Attendance 
from django.contrib.admin import ModelAdmin


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'get_lesson_schedule', 'get_study_center', 'date', 'is_present', 'locked')
    list_display_links = ('id', 'student')
    search_fields = ('student__first_name', 'student__last_name', 'lesson_schedule__lesson__group__name', 'study_center__name')
    list_filter = ('is_present', 'locked', 'lesson_schedule__day', 'study_center')

    def get_lesson_schedule(self, obj):
        return obj.lesson_schedule.lesson.group.name
    get_lesson_schedule.short_description = "Dars jadvali (Guruh)"

    def get_study_center(self, obj):
        return obj.study_center.name if obj.study_center else "Noma'lum"
    get_study_center.short_description = "O'quv markaz"


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(ModelAdmin):
    list_display = ('id', 'get_group_name', 'get_study_center_name', 'date', 'is_completed')
    list_display_links = ('id', 'get_group_name')
    search_fields = ('group__name', 'study_center__name')  # Use actual fields for search
    list_filter = ('group__study_center', 'is_completed')  # Use related fields for filtering

    def get_group_name(self, obj):
        return obj.group.name
    get_group_name.short_description = "Guruh nomi"

    def get_study_center_name(self, obj):
        return obj.study_center.name
    get_study_center_name.short_description = "O'quv markaz"


@admin.register(Days)
class DaysAdmin(ModelAdmin):
    list_display = ('id', 'name')
    list_filter = ('id', )
    search_fields = ('name', )

@admin.register(LessonSchedule)
class LessonScheduleAdmin(ModelAdmin):
    list_display = ('id', 'lesson_group_name', 'day', 'time', 'get_study_center')
    list_filter = ('day', 'lesson__study_center')  # Use lesson__study_center for filtering
    list_display_links = ('id', 'lesson_group_name')
    search_fields = ('lesson__group__name', 'lesson__study_center__name')

    def lesson_group_name(self, obj):
        return obj.lesson.group.name
    lesson_group_name.short_description = "Dars guruhi"

    def get_study_center(self, obj):
        return obj.lesson.study_center.name
    get_study_center.short_description = "O'quv markaz"


@admin.register(LessonsTable)
class LessonTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'study_center_name', 'group_name')
    list_display_links = ('id', 'study_center_name')
    search_fields = ('study_center__name', 'group__name')

    def study_center_name(self, obj):
        return obj.study_center.name
    study_center_name.short_description = "O'quv markaz"

    def group_name(self, obj):
        return obj.group.name
    group_name.short_description = "Guruh"




# FanlarAdmin
@admin.register(Fanlar)
class FanlarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_teacher_name', 'study_center')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'teacher__first_name')
    list_filter = ('study_center', )

    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.first_name
        return '-'
    get_teacher_name.short_description = "O'qituvchi ismi"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('teacher')

@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('id',  'amount', 'created_date')
    list_display_links = ('id', )


# GroupAdmin
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_fan_nomi', 'get_teacher_name', 'study_center', 'created_at', 'update_at')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'fan__name', 'teachers__first_name')
    list_filter = ('fan__name', 'teachers__first_name')
    prepopulated_fields = {'slug': ('name',)}

    def get_fan_nomi(self, obj):
        # `ManyToManyField` bo'lgan `fan` obyektidan birinchi elementni olish
        return obj.fan.first().name if obj.fan.exists() else '-'
    get_fan_nomi.short_description = 'Fan Nomi'

    def get_teacher_name(self, obj):
        # `ManyToManyField` bo'lgan `fan` obyektidan birinchi elementning ustozini olish
        if obj.fan.exists():
            fan = obj.fan.first()
            if fan.teacher:
                return fan.teacher.first_name
        return '-'
    get_teacher_name.short_description = 'Ustoz'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('fan', 'teachers')

# StudyCenterAdmin
@admin.register(StudyCenter)
class StudyCenterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'admin', 'address')
    list_display_links = ('id', 'name')
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}

# StudentAdmin
