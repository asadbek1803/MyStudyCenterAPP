import uuid
from django.db import models
from study_center.models import StudyCenter
from django.db.models import JSONField  # Django 3.1+ uchun umumiy JSONField


class ExamFan(models.Model):
    name = models.CharField(max_length=200)
    study_center = models.ForeignKey(StudyCenter, on_delete=models.CASCADE)
    ball = models.FloatField()  # Maksimal ball

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Imtihon Fanlari"
        verbose_name_plural = "Imtihon Fanlari"
        ordering = ['-ball']  # Orders messages by the most recent first


class Imtihonlar(models.Model):
    name = models.CharField(max_length=500)
    study_center = models.ForeignKey(StudyCenter, on_delete=models.CASCADE)
    fans = models.ManyToManyField(ExamFan)
    
    # related_name qo'shildi
    students = models.ManyToManyField('accounts.Account', related_name='student_exams')
    teachers = models.ManyToManyField('accounts.Account', related_name='teacher_exams')
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    exam_token = models.UUIDField(default=uuid.uuid4, unique=True)


    def registration_link(self):
        return f"/exams/registration/exam/study_center/{self.exam_token}/"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Imtihonlar"
        verbose_name_plural = "Imtihonlar"
        ordering = ['-date']  # Orders messages by the most recent first

class StudentResult(models.Model):
    student = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    checker = models.ForeignKey('accounts.Account', related_name='checked_results', on_delete=models.CASCADE)
    exam = models.ForeignKey(Imtihonlar, on_delete=models.CASCADE)

    # Postgres uchun JSONField o'rniga umumiy JSONField
    results = JSONField()  # {"Tarix": 38.6, "Ona tili": 85.1}

    def __str__(self):
        return f"{self.student.username} - {self.exam.name}"

    class Meta:
        verbose_name = "O'quvchi Natijalari"
        verbose_name_plural = "O'quvchi Natijalari"
        # ordering = ['-added_at']  # Orders messages by the most recent first

    @property
    def total_score(self):
        return sum(self.results.values())  # Barcha fanlardan jami ball

    @property
    def percentage(self):
        total_possible = len(self.exam.fans.all()) * 100  # Har bir fan uchun maksimal ball 100
        return (self.total_score / total_possible) * 100
