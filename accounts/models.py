import random
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from study_center.models import StudyCenter
# Create your models here.
from simple_history.models import HistoricalRecords
from study_center.models import Fanlar, Group




class MyAccountManager(BaseUserManager):
    def create_user(self, username, first_name, last_name, password=None, **extra_fields):
        
        if not username:
            raise ValueError("Username kiritish zarur!")
        
        if not password:
            raise ValueError("Parolni kiritish zarur!")
        
        elif not first_name and not last_name:
            raise ValueError("Siz Ism va Familyani kiritmadingiz!")

      
        user_id = ''.join(random.choices('0123456789ABCD', k=8))
        while self.model.objects.filter(user_id=user_id).exists():
            user_id = ''.join(random.choices('0123456789ABCD', k=8))

        extra_fields['user_id'] = user_id  # user_id ni extra_fields ga qo'shamiz
      
        user = self.model(
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, password):
        user = self.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.is_superadmin = True
        user.save(using = self._db)
        return user


class Account(AbstractBaseUser):
    roles = (
        
        ('director', 'director'),
        ('teacher', 'teacher'),
        ('student', 'student')
    )

    
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    user_id = models.CharField(max_length=10, unique=True, editable=False, blank=True, null=True)
    username   = models.CharField(max_length=50, unique=True)
    email      = models.EmailField(max_length=80, unique=True, blank=True, null=True)
    phone      = models.CharField(max_length=50)
    profile_image = models.FileField(upload_to='images/user/profile/', blank=True, null=True)
    total_score = models.FloatField(null=True, blank=True, default=0)
    month_score = models.FloatField(null=True, blank=True, default=0)
    groups = models.ManyToManyField(Group, related_name='account_groups', blank=True)
    fanlar = models.ManyToManyField(Fanlar, related_name='accounts', blank=True)
    telegram_user_id = models.IntegerField(blank=True, null=True)
    phone_home = models.CharField(max_length=50, blank=True, null=True)
    role       = models.CharField(max_length=29, choices=roles)
    studying = models.ForeignKey(StudyCenter, on_delete=models.CASCADE, blank=True, null=True, related_name='for_student')
    description = models.TextField(blank=True, null=True)
    address    = models.CharField(max_length=300, blank=True, null=True)
    study_center = models.ForeignKey(StudyCenter, on_delete=models.CASCADE, null=True, blank=True, related_name='for_driector')
    # Kerakli
    last_payment_date = models.DateTimeField(blank=True, null=True)
    history = HistoricalRecords()
    is_grand = models.BooleanField(default=False, null=True, blank=True)
    is_payed = models.BooleanField(default=False, blank=True, null=True)
    is_teacher = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login  = models.DateTimeField(auto_now_add=True)
    is_leave = models.BooleanField(default=False)
    is_admin    = models.BooleanField(default=False)
    is_staff    = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)
    
   

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = MyAccountManager()
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    
    
    
    
    def has_perm(self, perm, obj = None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True



class NotifactionMessage(models.Model):
    message = models.TextField()
    sender = models.ForeignKey(Account, on_delete=models.DO_NOTHING)
    receiver = models.ManyToManyField(Account, related_name='notifaction')
    sending_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.first()} {self.receiver.last()}: {self.message[:30]}..."

    class Meta:
        verbose_name = "Foydalanuvchi Xabarlari"
        verbose_name_plural = "Foydalanuvchi Xabarlari"
        ordering = ['-sending_date']  # Orders messages by the most recent first
    