# contact/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # 1. Ce qu'on voit dans la liste des messages
    list_display = (
        'full_name', # Propriété custom définie dans le modèle
        'email', 
        'subject', 
        'display_is_read', # Indicateur visuel Lu/Non Lu
        'replied_at',
        'created_at'
    )
    
    # 2. Liens pour cliquer et éditer
    list_display_links = ('full_name', 'subject',)
    
    # 3. Filtres sur le côté droit
    list_filter = ('is_read', 'replied_at', 'created_at',)
    
    # 4. Barre de recherche (Nom, Email, Sujet)
    search_fields = ('first_name', 'last_name', 'email', 'subject', 'message')
    
    # 5. Ordre par défaut (du plus récent au plus ancien)
    ordering = ('-created_at',)
    
    # 6. Organisation du formulaire d'édition
    fieldsets = (
        ('Informations de l\'expéditeur', {
            'fields': (('first_name', 'last_name'), 'email', 'subject', 'created_at')
        }),
        ('Contenu du message', {
            'fields': ('message',),
            'description': "Le contenu brut du message envoyé par l'utilisateur."
        }),
        ('Gestion du suivi', {
            'fields': ('is_read', 'replied_at', 'admin_notes', 'updated_at'),
        }),
    )

    # 7. Champs en lecture seule (les champs soumis ne doivent pas être modifiables)
    readonly_fields = ('first_name', 'last_name', 'email', 'subject', 'message', 'created_at', 'updated_at')
    
    # 8. Actions en haut (permet de marquer plusieurs messages comme lus en une seule fois)
    actions = ['mark_as_read', 'mark_as_unread', 'mark_as_replied']

    # --- Méthodes Personnalisées ---

    @admin.display(description="Lu")
    def display_is_read(self, obj):
        """Affiche un indicateur coloré pour le statut 'Lu'"""
        if obj.is_read:
            color = 'green'
            text = 'Oui'
        else:
            color = 'red'
            text = 'Non'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )

    # --- Actions personnalisées (Batch updates) ---

    @admin.action(description='Marquer les messages sélectionnés comme Lus')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} messages marqués comme lus.")

    @admin.action(description='Marquer les messages sélectionnés comme Non Lus')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} messages marqués comme non lus.")

    @admin.action(description='Marquer les messages sélectionnés comme Répondus (aujourd\'hui)')
    def mark_as_replied(self, request, queryset):
        queryset.update(replied_at=timezone.now())
        self.message_user(request, f"{queryset.count()} messages marqués comme répondus.")