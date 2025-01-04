from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User, Family, WishList, WishListItem, Notification
from .serializers import (
    UserSerializer, FamilySerializer, WishListSerializer,
    WishListItemSerializer, NotificationSerializer
)
from django.db.models import Q
from django.utils import timezone
from .utils.scraper import ProductScraper

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return users that share families with the current user
        return User.objects.filter(
            families__members=self.request.user
        ).distinct().exclude(id=self.request.user.id)

    @action(detail=False, methods=['GET'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 3:
            return Response([])
            
        users = User.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query)
        ).exclude(id=request.user.id)[:10]
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)

class FamilyViewSet(viewsets.ModelViewSet):
    serializer_class = FamilySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Family.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['POST'])
    def add_member(self, request, pk=None):
        family = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        family.members.add(user)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def remove_member(self, request, pk=None):
        family = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        family.members.remove(user)
        return Response(status=status.HTTP_200_OK)

class WishListViewSet(viewsets.ModelViewSet):
    serializer_class = WishListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Filter by family if provided
        family_id = self.request.query_params.get('family')
        # Filter by owner if provided
        owner_id = self.request.query_params.get('owner')
        
        queryset = WishList.objects.filter(family__members=user)
        
        if family_id:
            queryset = queryset.filter(family_id=family_id)
        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)
            
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        user = request.user
        wishlists = WishList.objects.filter(owner=user)
        
        # Get all items from user's wishlists
        items = WishListItem.objects.filter(wishlist__owner=user)
        
        # Get all families user is a member of
        families = user.families.all()
        
        return Response({
            'totalWishlists': wishlists.count(),
            'totalItems': items.count(),
            'purchasedItems': items.filter(is_purchased=True).count(),
            'totalFamilies': families.count(),
        })

    @action(detail=False, methods=['GET'])
    def recent_activity(self, request):
        user = request.user
        
        # Get items from families user is a member of, but exclude user's own wishlists
        items = WishListItem.objects.filter(
            # Put all filter conditions inside Q objects
            Q(wishlist__family__members=user) & 
            ~Q(wishlist__owner=user)
        ).select_related(
            'wishlist__owner',
            'purchased_by'
        ).order_by('-created_at')[:10]
        
        activity = []
        for item in items:
            if item.is_purchased and item.purchased_by:
                activity.append({
                    'id': f'purchase_{item.id}',
                    'title': f'{item.purchased_by.username} purchased {item.title}',
                    'date': item.purchased_at,
                    'color': 'success',
                    'userId': item.purchased_by.id,
                    'wishlistOwnerId': item.wishlist.owner.id
                })
            else:
                activity.append({
                    'id': f'add_{item.id}',
                    'title': f'{item.wishlist.owner.username} added {item.title}',
                    'date': item.created_at,
                    'color': 'info',
                    'userId': item.wishlist.owner.id,
                    'wishlistOwnerId': item.wishlist.owner.id
                })
        
        return Response(activity)

class WishListItemViewSet(viewsets.ModelViewSet):
    serializer_class = WishListItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishListItem.objects.filter(
            wishlist__family__members=self.request.user
        ).select_related('purchased_by', 'wishlist__owner')

    def perform_create(self, serializer):
        # Ensure image_url is saved from form data
        image_url = self.request.data.get('image_url', '')
        serializer.save(image_url=image_url)

    def perform_update(self, serializer):
        # Ensure image_url is updated from form data
        image_url = self.request.data.get('image_url', '')
        if image_url:
            serializer.save(image_url=image_url)
        else:
            serializer.save()

    @action(detail=True, methods=['POST'])
    def purchase(self, request, pk=None):
        item = self.get_object()
        if item.is_purchased:
            return Response(
                {'detail': 'Item is already purchased'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        item.is_purchased = True
        item.purchased_by = request.user
        item.purchased_at = timezone.now()
        item.save()
        
        # Return the updated item with nested purchased_by data
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def unpurchase(self, request, pk=None):
        item = self.get_object()
        if not item.is_purchased:
            return Response(
                {'detail': 'Item is not purchased'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        item.is_purchased = False
        item.purchased_by = None
        item.purchased_at = None
        item.save()
        
        # Return the updated item
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def scrape_url(self, request):
        url = request.data.get('url')
        if not url:
            return Response(
                {'error': 'URL is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            scraper = ProductScraper(url)
            data = scraper.scrape()

            if not data:
                return Response(
                    {'error': 'Failed to scrape URL'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['POST'])
    def reorder_items(self, request):
        wishlist_id = request.data.get('wishlist_id')
        item_ids = request.data.get('item_ids', [])
        
        if not wishlist_id or not item_ids:
            return Response(
                {'detail': 'Wishlist ID and item IDs are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user has access to this wishlist
        wishlist = WishList.objects.filter(
            id=wishlist_id,
            family__members=request.user
        ).first()
        
        if not wishlist:
            return Response(
                {'detail': 'Wishlist not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update priority for each item
        for index, item_id in enumerate(item_ids):
            WishListItem.objects.filter(
                id=item_id, 
                wishlist=wishlist
            ).update(priority=index)
        
        # Return the updated items
        items = WishListItem.objects.filter(wishlist=wishlist).order_by('priority')
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['POST'])
    def mark_all_read(self, request):
        self.get_queryset().update(read=True)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        user = request.user
        wishlists = WishList.objects.filter(owner=user)
        items = WishListItem.objects.filter(wishlist__owner=user)
        
        return Response({
            'totalWishlists': wishlists.count(),
            'totalItems': items.count(),
            'purchasedItems': items.filter(is_purchased=True).count(),
            'totalFamilies': user.families.count(),
        })

    @action(detail=False, methods=['GET'])
    def recent_activity(self, request):
        user = request.user
        
        # Get recent items from user's families
        items = WishListItem.objects.filter(
            wishlist__family__members=user
        ).order_by('-created_at')[:10]
        
        activity = []
        for item in items:
            if item.is_purchased:
                activity.append({
                    'id': f'purchase_{item.id}',
                    'title': f'{item.purchased_by.username} purchased {item.title}',
                    'date': item.purchased_at,
                    'color': 'success'
                })
            else:
                activity.append({
                    'id': f'add_{item.id}',
                    'title': f'{item.wishlist.owner.username} added {item.title}',
                    'date': item.created_at,
                    'color': 'info'
                })
        
        return Response(activity) 