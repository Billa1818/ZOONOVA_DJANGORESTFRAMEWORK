
# ============================================
# 2. APP BOOKS - Serializers Catalogue
# ============================================

from rest_framework import serializers
from .models import Book


class BookListSerializer(serializers.ModelSerializer):
    """Serializer pour liste de livres"""
    
    prix_euros = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    in_stock = serializers.BooleanField(read_only=True)
    main_image = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'titre', 'nom', 'legende', 'slug',
            'prix', 'prix_euros', 'quantites', 'in_stock',
            'main_image', 'is_featured', 'views_count', 'sales_count', 'videos'
        ]
    
    def get_main_image(self, obj):
        """Retourne l'URL de l'image principale"""
        main_image = obj.images.filter(is_main_cover=True).first()
        if main_image and main_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_image.image.url)
        return None
    
    def get_videos(self, obj):
        """Retourne toutes les vidéos du livre"""
        from media.serializers import BookVideoSerializer
        return BookVideoSerializer(
            obj.videos.all(),
            many=True,
            context=self.context
        ).data


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un livre"""
    
    prix_euros = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    in_stock = serializers.BooleanField(read_only=True)
    dimensions = serializers.CharField(read_only=True)
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'titre', 'nom', 'description', 'legende',
            'prix', 'prix_euros', 'code_bare', 'nombre_pages',
            'largeur_cm', 'hauteur_cm', 'epaisseur_cm',
            'poids_grammes', 'dimensions', 'date_publication',
            'editeur', 'langue', 'quantites', 'in_stock',
            'slug', 'seo_title', 'seo_description',
            'views_count', 'sales_count', 'is_active',
            'is_featured', 'images', 'videos',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'prix_euros', 'in_stock', 'dimensions',
            'views_count', 'sales_count', 'created_at', 'updated_at'
        ]
    
    def get_images(self, obj):
        """Retourne toutes les images du livre"""
        from media.serializers import BookImageSerializer
        return BookImageSerializer(
            obj.images.all(),
            many=True,
            context=self.context
        ).data
    
    def get_videos(self, obj):
        """Retourne toutes les vidéos du livre"""
        from media.serializers import BookVideoSerializer
        return BookVideoSerializer(obj.videos.all(), many=True).data


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour création/modification de livre"""
    
    class Meta:
        model = Book
        fields = [
            'id','titre', 'nom', 'description', 'legende',
            'prix', 'code_bare', 'nombre_pages',
            'largeur_cm', 'hauteur_cm', 'epaisseur_cm',
            'poids_grammes', 'date_publication', 'editeur',
            'langue', 'quantites', 'seo_title', 'seo_description',
            'is_active', 'is_featured'
        ]
    
    def validate_prix(self, value):
        """Valide que le prix est positif"""
        if value < 0:
            raise serializers.ValidationError("Le prix doit être positif")
        return value
    
    def validate_quantites(self, value):
        """Valide que la quantité est positive"""
        if value < 0:
            raise serializers.ValidationError("La quantité doit être positive")
        return value


class BookStockSerializer(serializers.ModelSerializer):
    """Serializer pour mise à jour du stock uniquement"""
    
    class Meta:
        model = Book
        fields = ['id', 'titre', 'quantites', 'in_stock']
        read_only_fields = ['id', 'titre', 'in_stock']