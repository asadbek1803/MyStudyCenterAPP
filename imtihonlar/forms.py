from django import forms
from .models import StudentResult
from accounts.models import Account

class StudentResultForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = ['student', 'checker', 'exam', 'results']

    def __init__(self, *args, **kwargs):
        # `request`ni kwargs'dan olish
        self.request = kwargs.pop('request', None)
        super(StudentResultForm, self).__init__(*args, **kwargs)

        # `student` fieldida faqat foydalanuvchining study_center'iga oid o'quvchilarni ko'rsatish
        if self.request:
            study_center = self.request.user.study_center
            self.fields['student'].queryset = Account.objects.filter(study_center=study_center, role='student')

        # `checker` fieldini request.user bilan to'ldirish va disabled qilish
        if self.request:
            self.fields['checker'].initial = self.request.user
            self.fields['checker'].disabled = True  # Bu maydonni o'zgartirib bo'lmaydigan qilish