from django.contrib import admin
from .models import ChatMessage, ChatSession, CustomUser
from django.core.mail import send_mail

# Register your models here.
admin.site.register(ChatMessage)
admin.site.register(ChatSession)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('username', 'email')
    ordering = ('username',)
    list_editable = ('is_active',)

    def save_model(self, request, obj, form, change):
        """Notify users about activation/deactivation or registration status."""

        # Send email only when activation status changes
        if change:
            old_user = CustomUser.objects.get(pk=obj.pk)
            if old_user.is_active != obj.is_active:
                if obj.is_active:
                    subject = "Your account has been activated"
                    message = (
                        f"Hi {obj.username},\n\n"
                        "Your account has been activated by the admin. You can now log in.\n\n"
                        "Best regards,\nAdmin Team"
                    )
                else:
                    subject = "Your account has been deactivated"
                    message = (
                        f"Hi {obj.username},\n\n"
                        "Your account has been deactivated by the admin.\n"
                        "You won’t be able to log in until it’s reactivated.\n\n"
                        "Best regards,\nAdmin Team"
                    )

                send_mail(
                    subject,
                    message,
                    'admin@gmail.com',     # Sender
                    [obj.email],           # Recipient
                    fail_silently=False,
                )

        # Save the user normally
        super().save_model(request, obj, form, change)