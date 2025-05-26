# /home/ubuntu/platform-services/account_management_service/views.py                      # Autor: Szymon Fuchs
# Autor: Szymon Fuchs
# Data: 18.08.2021                                                                        
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
import json
from .models import EmailChangeRequest

EMAIL_CHANGE_TOKEN_LIFESPAN_SECONDS = 3600

class RequestEmailChangeView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user_id_from_request = data.get('user_id')
            new_email = data.get('new_email')
            current_password = data.get('current_password')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

        if not all([user_id_from_request, new_email, current_password]):
            return JsonResponse({'error': 'Missing required data: user_id, new_email, current_password.'}, status=400)

        User = get_user_model()
        try:
            user = User.objects.get(pk=user_id_from_request)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)

        if not user.check_password(current_password):
            return JsonResponse({'error': 'Invalid current password.'}, status=403)

        if not new_email or "@" not in new_email:
            return JsonResponse({'error': 'A valid new email address is required.'}, status=400)
            
        if user.email == new_email:
            return JsonResponse({'error': 'The new email address is the same as your current one.'}, status=400)

        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            return JsonResponse({'error': 'This email address is already in use by another account.'}, status=409)

        EmailChangeRequest.objects.filter(user=user, expires_at__gt=timezone.now()).delete()

        token_value = get_random_string(length=48)
        email_change_req = EmailChangeRequest.objects.create(
            user=user,
            new_email=new_email,
            token=token_value
        )
        
        verification_link = request.build_absolute_uri(
            reverse('confirm_email_change', kwargs={'token': token_value})
        )
        
        sender_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@twojadomena.pl')

        try:
            send_mail(
                'Potwierdź zmianę adresu e-mail / Confirm Email Address Change',
                f'Witaj {user.get_username()},\n\nAby potwierdzić zmianę adresu e-mail na {new_email}, kliknij poniższy link:\n{verification_link}\n\nLink wygaśnie za {EMAIL_CHANGE_TOKEN_LIFESPAN_SECONDS // 3600} godzin.\nJeśli to nie Ty inicjowałeś tej zmiany, zignoruj tę wiadomość.\n\n---\n\nHello {user.get_username()},\n\nTo confirm your email address change to {new_email}, please click the link below:\n{verification_link}\n\nThe link will expire in {EMAIL_CHANGE_TOKEN_LIFESPAN_SECONDS // 3600} hour(s).\nIf you did not initiate this change, please ignore this message.',
                sender_email,
                [new_email],
                fail_silently=False,
            )
            
            if user.email:
                send_mail(
                    'Zażądano zmiany adresu e-mail / Email Change Requested for Your Account',
                    f'Witaj {user.get_username()},\n\nOtrzymaliśmy żądanie zmiany adresu e-mail powiązanego z Twoim kontem na {new_email}.\nJeśli to Ty inicjowałeś tę zmianę, postępuj zgodnie z instrukcjami wysłanymi na nowy adres e-mail.\n\nJeśli to nie Ty, natychmiast zabezpiecz swoje konto i skontaktuj się z pomocą techniczną.\n\n---\n\nHello {user.get_username()},\n\nWe received a request to change the email address associated with your account to {new_email}.\nIf you initiated this change, please follow the instructions sent to your new email address.\n\nIf this was not you, please secure your account immediately and contact support.',
                    sender_email,
                    [user.email],
                    fail_silently=False,
                )
            
            return JsonResponse({'message': 'Verification email sent to the new address. Please also check your old email for a notification.'})
        except Exception as e:
            return JsonResponse({'error': f'Could not send verification email. Error: {str(e)}'}, status=500)


class ConfirmEmailChangeView(View):
    def get(self, request, token, *args, **kwargs):
        try:
            email_change_req = EmailChangeRequest.objects.get(token=token)
        except EmailChangeRequest.DoesNotExist:
            return HttpResponse('Invalid or expired token. Please request a new one.', status=400)

        if email_change_req.is_expired():
            email_change_req.delete() 
            return HttpResponse('This email change token has expired. Please request a new one.', status=400)

        User = get_user_model()
        try:
            user = email_change_req.user 
            new_email = email_change_req.new_email

            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                 email_change_req.delete()
                 return HttpResponse('This email address has been taken by another account since your request. Please try the process again with a different email.', status=409)
            
            user_previous_email = user.email
            user.email = new_email
            user.save(update_fields=['email'])
            email_change_req.delete()

            sender_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@twojadomena.pl')
            try:
                send_mail(
                    'Twój adres e-mail został pomyślnie zmieniony / Your Email Address Has Been Successfully Changed',
                    f'Witaj {user.get_username()},\n\nAdres e-mail dla Twojego konta został pomyślnie zmieniony na {new_email}.\n\n---\n\nHello {user.get_username()},\n\nYour email address for your account has been successfully changed to {new_email}.',
                    sender_email,
                    [new_email],
                    fail_silently=True,
                )
                if user_previous_email and user_previous_email != new_email:
                     send_mail(
                        'Powiadomienie o zmianie adresu e-mail / Notification of Email Address Change',
                        f'Witaj {user.get_username()},\n\nAdres e-mail dla Twojego konta został zmieniony z {user_previous_email} na {new_email}.\n\n---\n\nHello {user.get_username()},\n\nYour email address for your account was changed from {user_previous_email} to {new_email}.',
                        sender_email,
                        [user_previous_email],
                        fail_silently=True,
                    )
            except Exception:
                pass

            return HttpResponse('Your email address has been changed successfully.')
        except User.DoesNotExist:
            return HttpResponse('User associated with this token not found.', status=404)
        except Exception as e:
            return HttpResponse(f'An unexpected error occurred: {str(e)}', status=500)

