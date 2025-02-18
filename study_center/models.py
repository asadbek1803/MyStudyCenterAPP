from django.db import models
from django.template.defaultfilters import slugify
from simple_history.models import HistoricalRecords



class StudyCenter(models.Model):
    history = HistoricalRecords()
    admins = (
        (1, 'Admin 1'),
        (2, 'Admin 2'),
        (3, 'Admin 3')
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    teachers = models.ManyToManyField('accounts.Account', related_name='teaching_centers', blank=True)
    students = models.ManyToManyField('accounts.Account', related_name='learning_centers', blank=True)
    description = models.TextField()
    logo = models.ImageField(upload_to='images/StudyCenters/')
    admin = models.IntegerField(choices=admins)
    address = models.CharField(max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "O'quv markazlar"
        verbose_name_plural = "O'quv markazlar"
        # ordering = ['-price']  # Orders messages by the most

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while StudyCenter.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

class Fanlar(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, related_name='teaching_fanlar')
    study_center = models.ForeignKey(StudyCenter, blank=True, null=True, on_delete=models.CASCADE, related_name='study_center')
    history = HistoricalRecords()
    # Boshqa maydonlar...

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Fanlar"
        verbose_name_plural = "Fanlar"
        # ordering = ['-price']  # Orders messages by the most


class Days(models.Model):
    name = models.CharField(max_length=100)
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kunlar"
        verbose_name_plural = "Kunlar"
        # ordering = ['-price']  # Orders messages by the most




class Payments(models.Model):
    TYPE = (
        ("MAHSULOTGA", "MAHSULOTGA"),
        ("OYLIK TO'LOV UCHUN", "OYLIK TO'LOV UCHUN")
    )
    student = models.ForeignKey('accounts.Account', blank=True, null=True, on_delete=models.CASCADE,
                                related_name='student_payments')
    teacher = models.ForeignKey('accounts.Account', blank=True, null=True, on_delete=models.CASCADE,
                                related_name='teacher_payments')
    subject = models.ForeignKey(Fanlar, blank=True, null=True, on_delete=models.CASCADE)
    study_center = models.ForeignKey(StudyCenter, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.IntegerField()
    type = models.CharField(max_length=50, choices=TYPE)
    created_date = models.DateTimeField(auto_now_add=True)
    exp_date = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = "To'lovlar"
        verbose_name_plural = "To'lovlar"
        ordering = ['-created_date']  # Orders messages by the most

    @classmethod
    def student_payment_history(cls, student):
        return cls.objects.filter(student=student).order_by('-created_date')

    @staticmethod
    def student_last_payment(student):
        return Payments.objects.filter(student=student).order_by('-created_date').first()

    @classmethod
    def total_payments(cls, study_center=None):
        if study_center:
            return cls.objects.filter(study_center=study_center).aggregate(total=models.Sum('amount'))['total']
        return cls.objects.aggregate(total=models.Sum('amount'))['total']

class Group(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    students = models.ManyToManyField('accounts.Account', blank=True, related_name="group_students")
    teachers = models.ManyToManyField('accounts.Account', blank=True, related_name="group_teachers")
    study_center = models.ForeignKey(StudyCenter, null=True, on_delete=models.CASCADE, related_name="study_groups")
    description = models.TextField(blank=True, null=True)
    leave_student_counter = models.IntegerField(default=0, blank=True, null=True)
    history = HistoricalRecords()
    group_logo = models.ImageField(upload_to='images/group_logo/', blank=True, null=True)
    fan = models.ManyToManyField(Fanlar, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Guruhlar"
        verbose_name_plural = "Guruhlar"
        ordering = ['-created_at']  # Orders messages by the most

    def get_url(self):
        return f"/center/guruhlar/{self.slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

        # Update students in the group
        if self.pk:
            old_group = Group.objects.get(pk=self.pk)
            added_students = self.students.exclude(id__in=old_group.students.all())
            removed_students = old_group.students.exclude(id__in=self.students.all())

            # Add newly added students to the group
            for student in added_students:
                student.groups.add(self)

            # Remove students who were removed from the group
            for student in removed_students:
                student.groups.remove(self)


class LessonsTable(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    study_center = models.ForeignKey(StudyCenter, on_delete=models.CASCADE)

    def __str__(self):
        return f"O'quv markaz: {self.study_center.name} -> Guruh: {self.group.name}"
    
    class Meta:
        verbose_name = "Dars jadvallar"
        verbose_name_plural = "Dars jadvallar"
        # ordering = ['-created_at']  # Orders messages by the most


class LessonSchedule(models.Model):
    DAYS = (
        ('Dushanba', 'Dushanba'),
        ('Seshanba', 'Seshanba'),
        ('Chorshanba', 'Chorshanba'),
        ('Payshanba', 'Payshanba'),
        ('Juma', 'Juma'),
        ('Shanba', 'Shanba'),
        ('Yakshanba', 'Yakshanba'),
    )
    lesson = models.ForeignKey(LessonsTable, on_delete=models.CASCADE, related_name='schedules')
    day = models.CharField(max_length=10, choices=DAYS)
    time = models.TimeField()

    def __str__(self):
        return f"{self.lesson.group.name} - {self.day} {self.time}"

    class Meta:
        verbose_name = "Dars vaqtlari"
        verbose_name_plural = "Dars vaqtlari"

class Attendance(models.Model):
    student = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    lesson_schedule = models.ForeignKey(LessonSchedule, on_delete=models.CASCADE)
    study_center = models.ForeignKey(StudyCenter, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['student', 'lesson_schedule', 'date']

    def __str__(self):
        return f"{self.student} - {self.lesson_schedule} - {self.date}"

    class Meta:
        verbose_name = "Davomat"
        verbose_name_plural = "Davomat"

class AttendanceRecord(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    study_center = models.ForeignKey(StudyCenter, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField()
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ['group', 'study_center', 'date']

    def __str__(self):
        return f"{self.study_center} - {self.group} - {self.date}"

    class Meta:
        verbose_name = "Davomatlar Record"
        verbose_name_plural = "Davomat Record"
