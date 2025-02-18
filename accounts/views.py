import requests
import json
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Account, NotifactionMessage
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


logger = logging.getLogger(__name__)



# def SignIn(request):
#     if request.user.is_authenticated:
#         if request.user.role == 'student':
#             return redirect('student')
#         else:
#             return redirect('dashboard')

#     if request.method == 'POST':
#         # captcha_token = request.POST.get('g-recaptcha-response')
#         # captcha_url = "https://www.google.com/recaptcha/api/siteverify"
#         # captcha_key = "6Lf6pbUpAAAAADHj71xh2PZCCxHeMJsVm2dvQn4E"
#         # data = {
#         #     'secret': captcha_key,
#         #     'response': captcha_token
#         # }
        
        
#         # Kirishni bosqicha keldi
#         username = request.POST.get('secret')
#         password = request.POST.get('password')
        
#         if not username or not password:
#             messages.error(request, "Hamma maydonlarni to'ldirish shart!")
#             return redirect('login')
        
#         user = authenticate(request, identifier=username, password=password)
        
#         if user is not None:
#             if not user.is_active:
#                 messages.error(request, "Sizning akkauntingiz mamuriyat tomonidan bekor qilinang guruh rahbaringiz bilan aloqaga chiqing!")
#                 return redirect('/')
            
#             login(request, user)
#             if user.role == 'student':
#                 messages.success(request, "O'quvchi profiliga muvaffaqiyatli kirildi!")
#                 return redirect('student')
#             else:
#                 messages.success(request, "O'qituvchi profiliga muvaffaqiyatli kirildi!")
#                 return redirect('dashboard')
#         else:
#             messages.error(request, 'Parol yoki UserID xato!')

#     return render(request, 'auth/login.html')


def SignIn(request):
    # Agar foydalanuvchi allaqachon tizimga kirgan bo'lsa
    if request.user.is_authenticated:
        return redirect('student' if getattr(request.user, 'role', None) == 'student' else 'dashboard')

    if request.method == 'POST':
        username = request.POST.get('secret')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Hamma maydonlarni to'ldirish shart!")
            return redirect('login')

        # Foydalanuvchini autentifikatsiya qilish
        user = authenticate(request, identifier=username, password=password)

        if user:
            if not user.is_active:
                messages.error(request, "Sizning akkauntingiz bekor qilingan. Iltimos, guruh rahbari bilan bog'laning.")
                return redirect('login')

            # Foydalanuvchini tizimga kirgizish
            login(request, user)
            role = "O'quvchi" if getattr(user, 'role', None) == 'student' else "O'qituvchi"
            messages.success(request, f"{role} profiliga muvaffaqiyatli kirildi!")
            return redirect('student' if user.role == 'student' else 'dashboard')
        else:
            messages.error(request, 'Parol yoki UserID xato!')

    return render(request, 'auth/login.html')



@login_required
def SignOut(request): #Chiqish
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')
    else:
        return redirect('login')

@csrf_exempt
@require_POST
def save_firebase_token(request):
    token = request.POST.get('token')
    # Bu yerdagi `user`ni aniqlashni unutmang, masalan, sessiya orqali
    user = request.user
    if token and user.is_authenticated:
        # Tokenni foydalanuvchi bilan bog'liq holda bazada saqlang
        user.fcm_token = token
        user.save()
        return JsonResponse({'status': 'success', 'message': 'Token saved successfully'})
    return JsonResponse({'status': 'error', 'message': 'Token or user not found'}, status=400)
    


@login_required
def save_telegram_id(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            telegram_id = data.get('telegram_id')
            
            user = request.user
            user.telegram_user_id = telegram_id
            user.save()
            
            return JsonResponse({'success': True, 'message': 'Sessiya muvaffaqiyatli saqlandi!'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@login_required
def settings_view(request):
    if request.method == 'POST':
        # JSON formatda ma'lumotlarni olish
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            try:
                data = json.loads(request.body.decode('utf-8'))
                telegram_id = data.get('telegram_id')
                print(telegram_id)
                logger.info(f"Received Telegram ID: {telegram_id}")

                if telegram_id:
                    request.user.telegram_user_id = telegram_id
                    request.user.save()
                    return JsonResponse({'success': True, 'message': 'Telegram ID muvaffaqiyatli saqlandi'})
                else:
                    return JsonResponse({'success': False, 'message': 'Telegram ID mavjud emas'})
            except json.JSONDecodeError:
                logger.error("JSON decode error", exc_info=True)
                return JsonResponse({'success': False, 'message': 'Nototo\'g\'ri JSON formati'})
        
        # URL-encoded ma'lumotlar
        try:
            user = request.user
            user.telegram_user_id = request.POST.get('telegram_id', user.telegram_user_id)
            user.username = request.POST.get('username', user.username)
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.address = request.POST.get('address', user.address)
            user.email = request.POST.get('email', user.email)
            user.phone = request.POST.get('phone', user.phone)

            if request.FILES.get('profile_image'):
                user.profile_image = request.FILES.get('profile_image')

            user.save()
            messages.success(request, 'Profil muvaffaqiyatli yangilandi.')
            return redirect('settings')
        except Exception as e:
            logger.error(f"Error updating profile: {e}", exc_info=True)
            messages.error(request, f"Xatolik yuz berdi: {e}")
            return redirect('settings')

    # GET so'rovlarda yoki POST so'rovlar muvaffaqiyatli bajarilmagan hollarda
    return render(request, 'auth/settings.html')



@login_required
def send_notification(request, role):
    if request.user.role in ['director', 'teacher']:
        if role in ['teacher', 'student']:
            users = Account.objects.filter(role=role, study_center=request.user.study_center)

            if request.method == 'POST':
                message = request.POST.get('message')
                all_users = request.POST.get('send_to_all', 'off') == 'on'

                if all_users:
                    receivers = users
                else:
                    selected_users = request.POST.getlist('selected_users')
                    if not selected_users:
                        messages.error(request, f"Siz {role}larni tanlamadingiz!")
                        return redirect('notify_users', role=role)
                    receivers = Account.objects.filter(id__in=selected_users)

                # Yangi bildirishnomani saqlash
                notification = NotifactionMessage.objects.create(
                    message=message,
                    sender=request.user,
                )
                notification.receiver.set(receivers)
                notification.save()

                # WebSocket orqali bildirishnoma jo‘natish
                channel_layer = get_channel_layer()
                for user in receivers:
                    async_to_sync(channel_layer.group_send)(
                        f"notifications_{user.id}",
                        {
                            "type": "send_notification",
                            "message": message,
                        },
                    )

                messages.success(request, "Xabarlar muvaffaqiyatli yuborildi!")
                return redirect('notify_users', role=role)

            return render(request, 'xabarlar/send_notification.html', {'users': users})
        else:
            return redirect("block_error_page")
    else:
        return redirect('/')


@login_required
def get_latest_notification(request):
    notif = NotifactionMessage.objects.filter(receiver=request.user).order_by('-id').first()
    if notif:
        return JsonResponse({"message": notif.message})
    return JsonResponse({"message": None})