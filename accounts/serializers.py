# ============================================
# 1. APP ACCOUNTS - Serializers Admin
# ============================================

from rest_framework import serializers
from .models import Admin, UserSession
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password


class AdminSerializer(serializers.ModelSerializer):
    """Serializer complet pour Admin"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Admin
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'full_name']
    
    def get_full_name(self, obj):
        """Retourne nom complet"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class AdminCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création Admin avec mot de passe"""
    
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Admin
        fields = [
            'email', 'first_name', 'last_name',
            'password', 'password_confirm',
            'is_staff', 'is_superuser'
        ]
    
    def validate(self, data):
        """Valide que les mots de passe correspondent"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas'
            })
        return data
    
    def create(self, validated_data):
        """Crée un admin avec mot de passe hashé"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        admin = Admin(**validated_data)
        admin.set_password(password)
        admin.save()
        return admin


class AdminListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour listes"""
    
    class Meta:
        model = Admin
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer JWT personnalisé avec informations utilisateur
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)

        # Ajouter les informations de l'utilisateur
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_superuser': self.user.is_superuser,
        }
        
        return data


class SetPasswordSerializer(serializers.Serializer):
    """
    Serializer pour définir le mot de passe initial
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas'
            })
        return data


class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Serializer pour demander une réinitialisation de mot de passe
    """
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer pour confirmer la réinitialisation
    """
    token = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas'
            })
        return data


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer pour les sessions utilisateur"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    ip_address = serializers.CharField(allow_null=True, allow_blank=True, read_only=True)
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'user_email', 'created_at', 'expires_at',
            'ip_address', 'user_agent', 'is_active'
        ]
        read_only_fields = ['id', 'user_email', 'created_at', 'expires_at', 'ip_address', 'user_agent', 'is_active']