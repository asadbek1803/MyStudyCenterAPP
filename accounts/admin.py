from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import ModelAdmin
from .models import Account, NotifactionMessage
from django.utils.html import format_html

# Avvalgi AccountAdmin ro'yxatga olinganligini tekshiring va uni o'chiring
if admin.site.is_registered(Account):
    admin.site.unregister(Account)

class AccountAdmin(UserAdmin):
    list_display = ('username','user_id', 'first_name', 'last_name',  'email', 'phone', 'role', 'is_active', 'is_staff', 'is_admin')
    search_fields = ('username', 'user_id',  'first_name', 'last_name', 'email', 'phone', 'role')
    readonly_fields = ('date_joined','user_id',  'last_login',  )
    list_filter = ('role', )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name','email', 'address',  'user_id',  'study_center', 'phone', 'role', 'password1', 'password2')}
        ),
    )
    
    def display_full_name(self, obj):
        return format_html('<strong>{}</strong>', obj.get_full_name())
    display_full_name.short_description = 'Full Name'

    # Agar tarixda qo'shimcha ma'lumotlarni ko'rsatmoqchi bo'lsangiz
    def history_view(self, request, object_id, extra_context=None):
        from django.contrib.admin.utils import get_object_edit_url
        context = {
            **(extra_context or {}),
            'object_edit_url': get_object_edit_url(self.model, object_id)
        }
        return super().history_view(request, object_id, extra_context=context)

admin.site.register(Account, AccountAdmin)

@admin.register(NotifactionMessage)
class NotifactionMessageAdmin(ModelAdmin):
    list_display = ('id', 'sender', 'message', 'sending_date')
    list_display_links = ('id', 'sender', )
    search_fields = ('id', 'sender__username')  # Use sender__username or any appropriate field
    list_filter = ('is_read', )


