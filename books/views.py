# books/views.py

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.db import IntegrityError

from .models import Book
from media.models import BookImage, BookVideo
from .serializers import (
    BookListSerializer,
    BookDetailSerializer,
    BookCreateUpdateSerializer,
    BookStockSerializer
)
from media.serializers import (
    BookImageSerializer,
    BookImageCreateSerializer,
    BookVideoSerializer
)


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des livres
    GET: Public
    POST/PUT/PATCH/DELETE: Admin seulement
    """
    queryset = Book.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured', 'langue', 'editeur']
    search_fields = ['titre', 'nom', 'description', 'legende']
    ordering_fields = ['created_at', 'prix', 'views_count', 'sales_count']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookCreateUpdateSerializer
        elif self.action == 'update_stock':
            return BookStockSerializer
        return BookDetailSerializer
    
    def get_queryset(self):
        queryset = Book.objects.all()
        
        # Les non-admins ne voient que les livres actifs
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        
        # Filtres additionnels
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(prix__gte=int(min_price))
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(prix__lte=int(max_price))
        
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(quantites__gt=0)
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        """
        Récupérer un livre et incrémenter le compteur de vues
        """
        instance = self.get_object()
        
        # Incrémenter les vues (seulement pour les non-admins)
        if not request.user.is_authenticated or not request.user.is_staff:
            instance.views_count += 1
            instance.save(update_fields=['views_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_stock(self, request, pk=None):
        """
        Mettre à jour uniquement le stock
        """
        book = self.get_object()
        serializer = BookStockSerializer(book, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Stock mis à jour',
            'book': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """
        Activer/désactiver la mise en avant
        """
        book = self.get_object()
        book.is_featured = not book.is_featured
        book.save()
        
        return Response({
            'message': f'Livre {"mis en avant" if book.is_featured else "retiré de la mise en avant"}',
            'is_featured': book.is_featured
        })
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Activer/désactiver le livre
        """
        book = self.get_object()
        book.is_active = not book.is_active
        book.save()
        
        return Response({
            'message': f'Livre {"activé" if book.is_active else "désactivé"}',
            'is_active': book.is_active
        })
    
    @action(detail=True, methods=['get'])
    def order_status(self, request, pk=None):
        """
        Vérifier le statut des commandes liées au livre
        """
        book = self.get_object()
        
        order_items = book.order_items.all()
        
        if not order_items.exists():
            return Response({
                'message': 'Aucune commande liée à ce livre',
                'can_delete': True,
                'orders': []
            })
        
        orders_info = []
        pending_count = 0
        delivered_count = 0
        
        for item in order_items:
            status = item.order.status
            orders_info.append({
                'order_id': item.order.id,
                'status': status,
                'created_at': item.order.created_at,
                'delivered_at': item.order.delivered_at
            })
            
            if status == 'pending':
                pending_count += 1
            elif status == 'delivered':
                delivered_count += 1
        
        return Response({
            'book_id': book.id,
            'total_orders': len(orders_info),
            'pending': pending_count,
            'delivered': delivered_count,
            'can_delete': pending_count == 0,
            'orders': orders_info
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Supprimer un livre avec vérification des dépendances
        Permet la suppression seulement si toutes les commandes sont livrées
        """
        book = self.get_object()
        
        # Vérifier si le livre a des articles de commande
        if book.order_items.exists():
            # Vérifier si toutes les commandes sont livrées
            from django.db.models import Q
            
            pending_orders = book.order_items.filter(
                Q(order__status='pending')  # Commandes non livrées
            ).count()
            
            if pending_orders > 0:
                return Response({
                    'error': 'Impossible de supprimer ce livre',
                    'detail': f'Ce livre est référencé dans {pending_orders} commande(s) en attente de livraison. Veuillez d\'abord les livrer.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Si toutes les commandes sont livrées, supprimer les OrderItems associés
            book.order_items.all().delete()
        
        # Supprimer le livre
        try:
            book.delete()
            return Response({
                'message': 'Livre supprimé avec succès'
            }, status=status.HTTP_204_NO_CONTENT)
        except IntegrityError as e:
            return Response({
                'error': 'Impossible de supprimer ce livre',
                'detail': 'Le livre est référencé ailleurs dans le système.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # ============================================
    # GESTION DES IMAGES
    # ============================================
    
    @action(detail=True, methods=['get'])
    def images(self, request, pk=None):
        """
        Lister toutes les images d'un livre
        """
        book = self.get_object()
        images = book.images.all()
        serializer = BookImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_image(self, request, pk=None):
        """
        Ajouter une image à un livre
        """
        book = self.get_object()
        data = request.data
        
        serializer = BookImageCreateSerializer(data=data, context={'request': request, 'book_id': book.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(book=book)
        
        return Response({
            'message': 'Image ajoutée',
            'image': BookImageSerializer(serializer.instance, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """
        Supprimer une image
        """
        book = self.get_object()
        try:
            image = book.images.get(id=image_id)
            image.delete()
            return Response({
                'message': 'Image supprimée'
            }, status=status.HTTP_204_NO_CONTENT)
        except BookImage.DoesNotExist:
            return Response({
                'error': 'Image non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)
    
    # ============================================
    # GESTION DES VIDÉOS
    # ============================================
    
    @action(detail=True, methods=['get'])
    def videos(self, request, pk=None):
        """
        Lister toutes les vidéos d'un livre
        """
        book = self.get_object()
        videos = book.videos.all()
        serializer = BookVideoSerializer(videos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_video(self, request, pk=None):
        """
        Ajouter une vidéo à un livre
        """
        book = self.get_object()
        data = request.data
        
        serializer = BookVideoSerializer(data=data, context={'request': request, 'book_id': book.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(book=book)
        
        return Response({
            'message': 'Vidéo ajoutée',
            'video': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='videos/(?P<video_id>[^/.]+)')
    def delete_video(self, request, pk=None, video_id=None):
        """
        Supprimer une vidéo
        """
        book = self.get_object()
        try:
            video = book.videos.get(id=video_id)
            video.delete()
            return Response({
                'message': 'Vidéo supprimée'
            }, status=status.HTTP_204_NO_CONTENT)
        except BookVideo.DoesNotExist:
            return Response({
                'error': 'Vidéo non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)


# ============================================
# MEDIA VIEWSETS (optionnel - gestion directe)
# ============================================

class BookImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion directe des images
    """
    queryset = BookImage.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BookImageCreateSerializer
        return BookImageSerializer
    
    @action(detail=True, methods=['post'])
    def set_main_cover(self, request, pk=None):
        """
        Définir comme couverture principale
        """
        image = self.get_object()
        
        # Désactiver les autres couvertures principales
        BookImage.objects.filter(
            book=image.book,
            is_main_cover=True
        ).update(is_main_cover=False)
        
        # Activer celle-ci
        image.is_main_cover = True
        image.save()
        
        return Response({
            'message': 'Image définie comme couverture principale',
            'image': BookImageSerializer(image, context={'request': request}).data
        })


class BookVideoViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gestion des vidéos d'un livre
    Chaque vidéo est liée à un seul livre
    """
    serializer_class = BookVideoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre les vidéos par livre"""
        book_id = self.request.query_params.get('book')
        if book_id:
            return BookVideo.objects.filter(book_id=book_id)
        return BookVideo.objects.all()
    
    def get_serializer_context(self):
        """Ajoute book_id au contexte si présent"""
        context = super().get_serializer_context()
        book_id = self.request.query_params.get('book')
        if book_id:
            context['book_id'] = int(book_id)
        return context
    
    def perform_create(self, serializer):
        """S'assure que le livre est assigné"""
        book_id = self.request.query_params.get('book')
        if book_id:
            serializer.save(book_id=int(book_id))
        else:
            serializer.save()