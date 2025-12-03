from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Book
from media.admin import BookImageInline, BookVideoInline

# --- 1. Création du filtre personnalisé ---
class InventoryStatusFilter(admin.SimpleListFilter):
    title = _('État du stock') # Titre affiché dans la barre latérale
    parameter_name = 'inventory_status' # Paramètre dans l'URL

    def lookups(self, request, model_admin):
        """Définit les options de filtre disponibles"""
        return (
            ('in_stock', _('En stock')),
            ('out_of_stock', _('Rupture de stock')),
            ('low_stock', _('Stock faible (< 5)')),
        )

    def queryset(self, request, queryset):
        """Filtre la requête selon l'option choisie"""
        if self.value() == 'in_stock':
            return queryset.filter(quantites__gt=0)
        if self.value() == 'out_of_stock':
            return queryset.filter(quantites=0)
        if self.value() == 'low_stock':
            return queryset.filter(quantites__gt=0, quantites__lt=5)
        return queryset


# --- 2. Configuration de l'Admin ---
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Inlines pour les images et vidéos
    inlines = [BookImageInline, BookVideoInline]
    
    # Liste des colonnes
    list_display = (
        'titre', 
        'nom', 
        'display_prix_euros', 
        'display_stock_status', 
        'is_active', 
        'is_featured', 
        'updated_at'
    )
    
    list_display_links = ('titre',)
    
    # CORRECTION ICI : On utilise notre filtre personnalisé créé plus haut
    list_filter = (
        'is_active', 
        'is_featured', 
        'langue', 
        'date_publication',
        InventoryStatusFilter, # Utilisation de la classe filtre
    )
    
    search_fields = ('titre', 'nom', 'code_bare', 'editeur', 'slug')
    prepopulated_fields = {'slug': ('titre',)}
    
    # Organisation du formulaire (inchangée)
    fieldsets = (
        ('Informations Générales', {
            'fields': ('titre', 'slug', 'nom', 'description', 'legende')
        }),
        ('Commerce', {
            'fields': (('prix', 'display_prix_hint'), 'quantites', 'is_active', 'is_featured'),
            'description': "Le prix doit être entré en centimes (ex: 2500 pour 25.00€)."
        }),
        ('Détails Éditoriaux', {
            'fields': ('editeur', 'date_publication', 'langue', 'code_bare', 'nombre_pages'),
            'classes': ('collapse',),
        }),
        ('Caractéristiques Physiques', {
            'fields': (('largeur_cm', 'hauteur_cm', 'epaisseur_cm'), 'poids_grammes'),
            'classes': ('collapse',),
        }),
        ('Référencement (SEO)', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',),
        }),
        ('Statistiques & Dates', {
            'fields': ('views_count', 'sales_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = (
        'display_prix_hint', 
        'views_count', 
        'sales_count', 
        'created_at', 
        'updated_at'
    )
    
    save_on_top = True

    # --- Méthodes Personnalisées ---

    @admin.display(description="Prix (€)")
    def display_prix_euros(self, obj):
        return f"{obj.prix / 100:.2f} €"

    @admin.display(description="Stock")
    def display_stock_status(self, obj):
        if obj.quantites == 0:
            color = 'red'
            text = 'Rupture'
        elif obj.quantites < 5:
            color = 'orange'
            text = f'Faible ({obj.quantites})'
        else:
            color = 'green'
            text = f'{obj.quantites}'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )

    @admin.display(description="Aperçu prix")
    def display_prix_hint(self, obj):
        if obj.prix:
            return f"Soit {obj.prix / 100:.2f} €"
        return "0.00 €"