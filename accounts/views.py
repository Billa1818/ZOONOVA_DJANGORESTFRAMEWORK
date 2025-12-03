# accounts/views.py

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import secrets
import jwt
from datetime import datetime

from .models import Admin, UserSession
from .serializers import (
    AdminSerializer,
    AdminCreateSerializer,
    AdminListSerializer,
    CustomTokenObtainPairSerializer,
    SetPasswordSerializer,
    RequestPasswordResetSerializer,
    PasswordResetConfirmSerializer,
    UserSessionSerializer
)

Admin = get_user_model()


def _get_client_ip(request):
    """Récupérer l'IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def _create_user_session(request, user, access_token):
    """Créer une session utilisateur après authentification"""
    try:
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        decoded = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        jti = decoded.get('jti', '')
        
        if jti:
            UserSession.objects.create(
                user=user,
                token_jti=jti,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=timezone.now() + timezone.timedelta(hours=1)
            )
    except Exception as e:
        # Log l'erreur mais ne pas bloquer
        pass


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vue personnalisée pour l'authentification JWT
    Gère le cas où l'admin n'a pas encore de mot de passe
    et crée automatiquement une session
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            
        except Exception as e:
            # Vérifier si c'est un compte sans mot de passe
            email = request.data.get('email')
            if email:
                try:
                    admin = Admin.objects.get(email=email)
                    if not admin.has_usable_password():
                        return Response({
                            'error': 'first_login',
                            'message': 'Première connexion. Veuillez définir votre mot de passe.',
                            'email': email

                        }, status=status.HTTP_403_FORBIDDEN)
                except Admin.DoesNotExist:
                    pass
            
            return Response({
                'error': 'invalid_credentials',
                'message': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Créer la session après authentification réussie
        response_data = serializer.validated_data
        user = serializer.user
        access_token = response_data.get('access')
        
        _create_user_session(request, user, access_token)
        
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def set_initial_password(request):
    """
    Définir le mot de passe lors de la première connexion
    et créer une session
    """
    serializer = SetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    try:
        admin = Admin.objects.get(email=email)
        
        # Vérifier que c'est bien une première connexion
        if admin.has_usable_password():
            return Response({
                'error': 'password_already_set',
                'message': 'Le mot de passe a déjà été défini'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Définir le mot de passe
        admin.set_password(password)
        admin.first_name = serializer.validated_data.get('first_name', '')
        admin.last_name = serializer.validated_data.get('last_name', '')
        admin.save()
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(admin)
        access_token = str(refresh.access_token)
        
        # Créer la session
        _create_user_session(request, admin, access_token)
        
        return Response({
            'message': 'Mot de passe défini avec succès',
            'tokens': {
                'refresh': str(refresh),
                'access': access_token,
            },
            'user': AdminSerializer(admin).data
        }, status=status.HTTP_200_OK)
        
    except Admin.DoesNotExist:
        return Response({
            'error': 'user_not_found',
            'message': 'Utilisateur introuvable'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Demander une réinitialisation de mot de passe
    """
    serializer = RequestPasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    
    try:
        admin = Admin.objects.get(email=email, is_active=True)
        
        # Générer un token de réinitialisation
        reset_token = secrets.token_urlsafe(32)
        admin.reset_password_token = reset_token
        admin.reset_password_token_created_at = timezone.now()
        admin.save()
        
        # Envoyer l'email
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
        
        context = {
            'admin': admin,
            'reset_url': reset_url,
        }
        
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = f"""
        Bonjour {admin.first_name or admin.email},
        
        Vous avez demandé une réinitialisation de mot de passe.
        
        Cliquez sur le lien suivant pour réinitialiser votre mot de passe :
        {reset_url}
        
        Ce lien expire dans 1 heure.
        
        Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
        """
        
        send_mail(
            subject='Réinitialisation de votre mot de passe',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return Response({
            'message': 'Email de réinitialisation envoyé'
        }, status=status.HTTP_200_OK)
        
    except Admin.DoesNotExist:
        # Pour des raisons de sécurité, on retourne toujours le même message
        return Response({
            'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    """
    Confirmer la réinitialisation du mot de passe
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    token = serializer.validated_data['token']
    password = serializer.validated_data['password']
    
    try:
        admin = Admin.objects.get(reset_password_token=token)
        
        # Vérifier que le token n'a pas expiré (1 heure)
        if admin.reset_password_token_created_at:
            token_age = timezone.now() - admin.reset_password_token_created_at
            if token_age.total_seconds() > 3600:  # 1 heure
                return Response({
                    'error': 'token_expired',
                    'message': 'Le lien de réinitialisation a expiré'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Définir le nouveau mot de passe
        admin.set_password(password)
        admin.reset_password_token = ''
        admin.reset_password_token_created_at = None
        admin.save()
        
        return Response({
            'message': 'Mot de passe réinitialisé avec succès'
        }, status=status.HTTP_200_OK)
        
    except Admin.DoesNotExist:
        return Response({
            'error': 'invalid_token',
            'message': 'Lien de réinitialisation invalide'
        }, status=status.HTTP_400_BAD_REQUEST)


class AdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des administrateurs
    Accessible uniquement aux superusers
    """
    queryset = Admin.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AdminCreateSerializer
        if self.action == 'list':
            return AdminListSerializer
        return AdminSerializer
    
    def get_queryset(self):
        queryset = Admin.objects.all()
        
        # Filtres
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_superuser = self.request.query_params.get('is_superuser')
        if is_superuser is not None:
            queryset = queryset.filter(is_superuser=is_superuser.lower() == 'true')
        
        return queryset.order_by('-date_joined')
    
    def create(self, request, *args, **kwargs):
        """
        Créer un nouvel admin (sans mot de passe)
        Un email sera envoyé pour configurer le compte
        """
        # Vérifier que l'utilisateur est superuser
        if not request.user.is_superuser:
            return Response({
                'error': 'permission_denied',
                'message': 'Seuls les superusers peuvent créer des administrateurs'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Créer l'admin sans mot de passe
        admin = Admin.objects.create(
            email=serializer.validated_data['email'],
            first_name=serializer.validated_data.get('first_name', ''),
            last_name=serializer.validated_data.get('last_name', ''),
            is_staff=serializer.validated_data.get('is_staff', True),
            is_superuser=serializer.validated_data.get('is_superuser', False),
        )
        
        # Envoyer l'email d'invitation
        setup_url = f"{settings.FRONTEND_URL}/setup-account"
        
        context = {
            'admin': admin,
            'setup_url': setup_url,
            'created_by': request.user,
        }
        
        html_message = render_to_string('emails/admin_invitation.html', context)
        plain_message = f"""
        Bonjour,
        
        Un compte administrateur a été créé pour vous sur la plateforme Bookstore.
        
        Email: {admin.email}
        
        Rendez-vous sur {setup_url} pour configurer votre mot de passe et accéder à votre compte.
        
        Cordialement,
        L'équipe Bookstore
        """
        
        send_mail(
            subject='Invitation - Compte Administrateur Bookstore',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return Response({
            'message': 'Administrateur créé avec succès. Un email d\'invitation a été envoyé.',
            'admin': AdminSerializer(admin).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Récupérer les informations de l'utilisateur connecté
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Activer/désactiver un admin
        """
        if not request.user.is_superuser:
            return Response({
                'error': 'permission_denied',
                'message': 'Seuls les superusers peuvent modifier le statut'
            }, status=status.HTTP_403_FORBIDDEN)
        
        admin = self.get_object()
        
        # Empêcher la désactivation de son propre compte
        if admin.id == request.user.id:
            return Response({
                'error': 'cannot_deactivate_self',
                'message': 'Vous ne pouvez pas désactiver votre propre compte'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        admin.is_active = not admin.is_active
        admin.save()
        
        return Response({
            'message': f'Compte {"activé" if admin.is_active else "désactivé"}',
            'admin': AdminSerializer(admin).data
        })
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Changer son propre mot de passe
        """
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({
                'error': 'missing_fields',
                'message': 'Ancien et nouveau mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not request.user.check_password(old_password):
            return Response({
                'error': 'invalid_password',
                'message': 'Mot de passe actuel incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({
            'message': 'Mot de passe modifié avec succès'
        })


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_sessions(request):
    """
    Gérer les sessions de l'utilisateur
    GET: Lister toutes les sessions actives
    POST: Invalider une session spécifique (session_id dans le corps)
    DELETE: Invalider toutes les sessions
    """
    
    # GET: Lister toutes les sessions
    if request.method == 'GET':
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        )
        serializer = UserSessionSerializer(sessions, many=True)
        return Response({
            'message': f'{len(sessions)} session(s) active(s)',
            'sessions': serializer.data
        }, status=status.HTTP_200_OK)
    
    # POST: Invalider une session spécifique
    elif request.method == 'POST':
        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({
                'error': 'missing_field',
                'message': 'session_id requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=request.user,
                is_active=True
            )
            session.is_active = False
            session.save()
            
            return Response({
                'message': 'Session invalidée avec succès'
            }, status=status.HTTP_200_OK)
        
        except UserSession.DoesNotExist:
            return Response({
                'error': 'session_not_found',
                'message': 'Session non trouvée ou déjà invalidée'
            }, status=status.HTTP_404_NOT_FOUND)
    
    # DELETE: Invalider toutes les sessions
    elif request.method == 'DELETE':
        sessions = UserSession.objects.filter(
            user=request.user,
            is_active=True
        )
        count = sessions.count()
        sessions.update(is_active=False)
        
        return Response({
            'message': f'{count} session(s) invalidée(s)',
            'sessions_invalidated': count
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all_devices(request):
    """
    Se déconnecter de tous les appareils (invalider toutes les sessions)
    """
    sessions = UserSession.objects.filter(
        user=request.user,
        is_active=True
    )
    count = sessions.count()
    sessions.update(is_active=False)
    
    return Response({
        'message': f'Déconnecté de tous les appareils ({count} session(s) invalidée(s))',
        'sessions_invalidated': count
    }, status=status.HTTP_200_OK)