# accounts/models.py (version mise à jour avec reset password et sessions)
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid
class AdminManager(BaseUserManager):
    """Manager pour les comptes administrateurs"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email requis')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class Admin(AbstractBaseUser, PermissionsMixin):
    """Compte administrateur uniquement - Pas de compte client"""
    email = models.EmailField(unique=True, db_index=True, verbose_name="Email")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Nom")
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    
    # Champs pour la réinitialisation du mot de passe
    reset_password_token = models.CharField(max_length=100, blank=True, verbose_name="Token de réinitialisation")
    reset_password_token_created_at = models.DateTimeField(null=True, blank=True, verbose_name="Token créé le")
    
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Date d'inscription")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")
    
    objects = AdminManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'admins'
        verbose_name = 'Administrateur'
        verbose_name_plural = 'Administrateurs'
    
    def __str__(self):
        return self.email


class UserSession(models.Model):
    """Modèle pour tracker les sessions des utilisateurs"""
    user = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='sessions')
    token_jti = models.CharField(max_length=255, unique=True, db_index=True)  # JWT JTI claim
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at}"