# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import NotificationV2

@receiver(post_save, sender=NotificationV2)
def send_notification_email(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        subject = f"Exposure Notification for {instance.disease}"
        message = f"Dear {user.username},\n\n{instance.message}\n\nStay safe!"
        recipient_list = [user.email]

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
