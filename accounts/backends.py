from django.contrib.auth.backends import BaseBackend
from .models import Account


class CustomBackend(BaseBackend):
    def authenticate(self, request, identifier=None, password=None, **kwargs):
        # Foydalanuvchini user_id, email yoki username orqali qidirish
        user = Account.objects.filter(user_id=identifier, role='student').first() or \
               Account.objects.filter(email=identifier, role='teacher').first() or \
               Account.objects.filter(username=identifier, role='director').first()
        
        # Agar foydalanuvchi topilgan bo'lsa va parol mos kelsa
        if user and user.check_password(password):
            return user
        return None

    def get_user(self, id):
        try:
            return Account.objects.get(pk=id)
        except Account.DoesNotExist:
            return None