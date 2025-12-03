# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Admin

class AdminUserAdmin(UserAdmin):
    # Définit le modèle associé
    model = Admin
    
    # Colonnes affichées dans la liste des utilisateurs
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'last_login')
    
    # Filtres disponibles dans la barre latérale
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    
    # Champs sur lesquels la barre de recherche fonctionne
    search_fields = ('email', 'first_name', 'last_name')
    
    # Tri par défaut
    ordering = ('email',)

    # Configuration du formulaire d'édition (Page de détail)
    # On remplace 'username' par 'email' et on ajoute vos champs personnalisés
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informations personnelles'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Dates importantes'), {'fields': ('last_login', 'date_joined')}),
        (_('Système de Reset Password'), {
            'classes': ('collapse',), # Masque cette section par défaut pour ne pas encombrer
            'fields': ('reset_password_token', 'reset_password_token_created_at'),
        }),
    )

    # Configuration du formulaire d'ajout (Bouton "Ajouter")
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'confirm_password'), # Nécessite une petite astuce ou form custom si on veut la confirmation
        }),
    )
    # Note: Pour add_fieldsets, UserAdmin gère généralement un formulaire spécial. 
    # Si vous voulez garder ça simple, on utilise souvent juste :
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'is_staff', 'is_active')}
        ),
    )

    # Empêcher la modification manuelle des tokens pour éviter de casser le flux de reset
    readonly_fields = ('reset_password_token', 'reset_password_token_created_at', 'last_login', 'date_joined')

admin.site.register(Admin, AdminUserAdmin)