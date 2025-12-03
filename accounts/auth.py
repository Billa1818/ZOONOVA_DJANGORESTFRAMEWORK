# accounts/auth.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import UserSession


class CustomJWTAuthentication(JWTAuthentication):
    """
    Authentificateur JWT personnalisé qui vérifie que la session est active
    """
    
    def authenticate(self, request):
        # Appeler l'authentification JWT standard
        result = super().authenticate(request)
        
        # Si pas d'authentification trouvée
        if result is None:
            return None
        
        user, validated_token = result
        
        # Récupérer le JTI du token
        jti = validated_token.get('jti')
        
        if not jti:
            raise AuthenticationFailed('Token invalide: JTI manquant')
        
        # Vérifier que la session existe et est active
        try:
            session = UserSession.objects.get(
                token_jti=jti,
                user=user,
                is_active=True
            )
        except UserSession.DoesNotExist:
            raise AuthenticationFailed('Session invalidée ou expirée')
        
        return user, validated_token
