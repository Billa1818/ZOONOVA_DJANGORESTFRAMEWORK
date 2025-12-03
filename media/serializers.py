# ============================================
# 3. APP MEDIA - Serializers Images/Vidéos
# ============================================

from rest_framework import serializers
from .models import BookImage, BookVideo


class BookImageSerializer(serializers.ModelSerializer):
    """Serializer pour images de livre"""
    
    image_url = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = BookImage
        fields = [
            'id', 'book', 'image', 'image_url', 'type',
            'type_display', 'is_main_cover', 'order',
            'alt_text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        """Retourne l'URL complète de l'image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class BookImageCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création d'image"""
    
    class Meta:
        model = BookImage
        fields = [
            'book', 'image', 'type', 'is_main_cover',
            'order', 'alt_text'
        ]
        extra_kwargs = {
            'book': {'required': False}
        }
    
    def validate(self, data):
        """Validation logique métier"""
        # Si c'est la couverture principale, vérifier unicité
        if data.get('is_main_cover', False):
            book = data.get('book')
            if book and BookImage.objects.filter(
                book=book,
                is_main_cover=True
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                # Le save() gérera la désactivation de l'ancienne
                pass
        return data
    
    def create(self, validated_data):
        """Create instance with book from context if not provided"""
        if 'book' not in validated_data and 'book_id' in self.context:
            validated_data['book_id'] = self.context['book_id']
        return super().create(validated_data)


class BookVideoSerializer(serializers.ModelSerializer):
    """Serializer pour vidéos de livre"""
    
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = BookVideo
        fields = [
            'id', 'book', 'video_file', 'video_url', 'title',
            'description', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'video_url']
        extra_kwargs = {
            'video_file': {'required': False}
        }
    
    def get_video_url(self, obj):
        """Retourne l'URL complète de la vidéo"""
        if obj.video_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None
    
    def create(self, validated_data):
        """Create instance with book from context if not provided"""
        if 'book' not in validated_data and 'book_id' in self.context:
            validated_data['book_id'] = self.context['book_id']
        return super().create(validated_data)