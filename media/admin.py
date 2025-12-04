# media/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import BookImage, BookVideo

# --- Inline pour les Images (BookImage) ---
class BookImageInline(admin.TabularInline):
    # TabularInline est plus compact que StackedInline
    model = BookImage
    extra = 1 # Affiche une ligne vide pour ajouter une nouvelle image par défaut
    
    # Ordre des champs à afficher
    fields = (
        'type', 
        'image', 
        'image_preview', # Aperçu de l'image (méthode custom)
        'alt_text', 
        'is_main_cover', 
        'order'
    )
    
    # Champs en lecture seule
    readonly_fields = ('image_preview',)
    
    @admin.display(description="Aperçu")
    def image_preview(self, obj):
        """Affiche une miniature de l'image si elle existe"""
        if obj.image:
            # Taille réduite pour l'admin (e.g., 100px de haut)
            return format_html(
                '<img src="{}" style="height: 100px; width: auto; border: 1px solid #ccc;" />', 
                obj.image.url
            )
        return "Pas d'image"

# --- Inline pour les Vidéos (BookVideo) ---
class BookVideoInline(admin.TabularInline):
    model = BookVideo
    extra = 1
    
    # Ordre des champs à afficher
    fields = ('title', 'video_file', 'description', 'order')

 
# --- Admin pour les Images (gestion directe) ---
@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    """
    Admin pour gérer les images directement
    Les images sont aussi gérées via inline dans BookAdmin
    """
    list_display = ('book', 'display_image', 'type', 'is_main_cover', 'order', 'created_at')
    list_filter = ('type', 'is_main_cover', 'created_at')
    search_fields = ('book__titre', 'alt_text')
    readonly_fields = ('created_at', 'updated_at', 'display_image_full')
    
    fieldsets = (
        ('Informations', {
            'fields': ('book', 'type', 'is_main_cover', 'order')
        }),
        ('Image', {
            'fields': ('image', 'display_image_full')
        }),
        ('Accessibilité', {
            'fields': ('alt_text',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description="Image")
    def display_image(self, obj):
        """Affiche une petite miniature dans la liste"""
        if obj.image:
            return format_html(
                '<img src="{}" style="height: 50px; width: auto; border-radius: 4px;" />', 
                obj.image.url
            )
        return "—"
    
    @admin.display(description="Aperçu de l'image")
    def display_image_full(self, obj):
        """Affiche l'image en pleine taille dans le formulaire"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 400px; border: 1px solid #ddd; border-radius: 4px;" />', 
                obj.image.url
            )
        return "Aucune image uploadée"


# --- Admin pour les Vidéos (gestion directe) ---
@admin.register(BookVideo)
class BookVideoAdmin(admin.ModelAdmin):
    """
    Admin pour gérer les vidéos directement
    Les vidéos sont aussi gérées via inline dans BookAdmin
    """
    list_display = ('book', 'title', 'display_video_file', 'order', 'created_at')
    list_filter = ('created_at', 'order')
    search_fields = ('book__titre', 'title')
    readonly_fields = ('created_at', 'updated_at', 'display_video_preview')
    
    fieldsets = (
        ('Informations', {
            'fields': ('book', 'title', 'order')
        }),
        ('Vidéo', {
            'fields': ('video_file', 'display_video_preview')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description="Fichier")
    def display_video_file(self, obj):
        """Affiche le nom du fichier vidéo avec lien"""
        if obj.video_file:
            return format_html(
                '<a href="{}" target="_blank" title="Télécharger">📹 {}</a>', 
                obj.video_file.url, obj.video_file.name.split('/')[-1]
            )
        return "—"
    
    @admin.display(description="Aperçu")
    def display_video_preview(self, obj):
        """Affiche un lecteur vidéo pour prévisualiser"""
        if obj.video_file:
            return format_html(
                '<video style="max-width: 300px; max-height: 300px; border: 1px solid #ddd; border-radius: 4px;" controls>'
                '<source src="{}" type="video/mp4">'
                'Votre navigateur ne supporte pas la balise vidéo'
                '</video>',
                obj.video_file.url
            )
        return "Aucune vidéo uploadée"