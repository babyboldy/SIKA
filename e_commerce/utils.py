"""
Utility functions for the SÎKÂ e-commerce platform.
"""
from django.core.mail import send_mail
from django.core import signing
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta


def send_email_verification(user, request):
    """
    Send email verification link to user using a simple token.
    """
    # Create a signed, timestamped token that encodes the user id
    token = signing.dumps({'uid': user.id}, salt='email-verify')
    
    from django.urls import reverse
    # Build absolute URL from named route to avoid hardcoded paths
    verification_link = request.build_absolute_uri(
        reverse('e_commerce:verify_email', args=[user.id, token])
    )
    
    subject = 'Confirmez votre compte SÎKÂ'
    message = f"""Bonjour {user.first_name},

Bienvenue sur SÎKÂ !

Merci de vous être inscrit. Pour activer votre compte et accéder à la plateforme,
veuillez cliquer sur le lien ci-dessous :

{verification_link}

Ce lien est valide pendant 24 heures.

Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.

Cordialement,
L'équipe SÎKÂ
"""
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list,
                  fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_order_confirmation(user, order):
    """
    Send order confirmation email to customer.
    """
    subject = f'Confirmation de commande #{order.order_number}'
    message = f"""
    Bonjour {user.first_name},
    
    Votre commande a été enregistrée avec succès !
    
    Détails de la commande :
    - Numéro : {order.order_number}
    - Date : {order.created_at.strftime('%d/%m/%Y à %H:%M')}
    - Montant total : {order.total_amount:.0f} FCFA
    - Méthode de paiement : {order.get_payment_method_display()}
    
    Nous vous contacterons bientôt pour confirmer votre commande.
    
    Merci pour votre confiance !
    L'équipe SÎKÂ
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list,
                  fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_seller_status_notification(user, status):
    """
    Send notification to user about their seller request status.
    """
    if status == 'approved':
        subject = 'Votre demande de vendeur a été approuvée'
        message = f"""
        Félicitations {user.first_name} !
        
        Votre demande pour devenir vendeur sur SÎKÂ a été approuvée.
        
        Vous pouvez maintenant accéder à votre tableau de bord vendeur
        et commencer à ajouter vos produits.
        
        Bienvenue dans l'équipe SÎKÂ !
        """
    else:
        subject = 'Statut de votre demande de vendeur'
        message = f"""
        Bonjour {user.first_name},
        
        Malheureusement, votre demande pour devenir vendeur n'a pas
        été approuvée pour le moment.
        
        Vous pouvez nous contacter pour plus d'informations.
        
        Cordialement,
        L'équipe SÎKÂ
        """
    
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list,
                  fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
