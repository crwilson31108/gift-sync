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
from django.contrib.auth.tokens import default_token_generator
from .utils.sendgrid_client import send_password_reset_email
from django.urls import reverse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

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

    @action(detail=False, methods=['POST'])
    def change_password(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response(
                {'detail': 'Both current and new password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(current_password):
            return Response(
                {'detail': 'Current password is incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set and save the new password
        user.set_password(new_password)
        user.save()
        
        return Response({'detail': 'Password changed successfully'})

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

    def perform_update(self, serializer):
        instance = self.get_object()
        
        # Get current priority if not provided in request
        priority = self.request.data.get('priority', instance.priority)
        
        # Handle image updates
        if 'image' in self.request.FILES:
            # New image file uploaded
            instance.image_url = ''  # Clear any existing image URL
            serializer.save(
                image=self.request.FILES['image'],
                priority=priority
            )
        elif 'image_url' in self.request.data and self.request.data['image_url']:
            # New image URL provided
            instance.image = None  # Clear any existing image file
            serializer.save(
                image_url=self.request.data['image_url'],
                priority=priority
            )
        else:
            # No new image, keep existing
            serializer.save(priority=priority)

    def perform_create(self, serializer):
        # Get the wishlist
        wishlist_id = self.request.data.get('wishlist')
        if wishlist_id:
            # Get the current highest priority for this wishlist
            highest_priority = WishListItem.objects.filter(
                wishlist_id=wishlist_id
            ).order_by('-priority').values_list('priority', flat=True).first()
            
            # Set priority to highest + 1, or 0 if no items exist
            priority = (highest_priority or -1) + 1
        else:
            priority = 0

        # Handle image creation with priority
        if 'image' in self.request.FILES:
            serializer.save(
                image=self.request.FILES['image'],
                priority=priority
            )
        elif 'image_url' in self.request.data and self.request.data['image_url']:
            serializer.save(
                image_url=self.request.data['image_url'],
                priority=priority
            )
        else:
            serializer.save(priority=priority)

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
        try:
            url = request.data.get('url')
            scraper = ProductScraper(url)
            data, error = scraper.scrape()
            
            if error:
                logger.error(f"Scraping error for URL {url}: {error}")
                return Response({
                    'error': 'Scraping failed',
                    'details': error,
                    'url': url
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(data)
        except Exception as e:
            logger.exception(f"Unexpected error while scraping {url}")
            return Response({
                'error': 'Unexpected error occurred',
                'message': str(e),
                'url': url
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    @action(detail=True, methods=['PATCH'])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

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

class PasswordResetViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def initial(self, request, *args, **kwargs):
        if request.method == 'OPTIONS':
            response = Response()
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            return response
        return super().initial(request, *args, **kwargs)
    
    @action(detail=False, methods=['POST'])
    def request_reset(self, request):
        print("\n=== Password Reset Request ===")
        print(f"FRONTEND_URL from settings: {settings.FRONTEND_URL}")
        print(f"DEBUG mode: {settings.DEBUG}")
        
        email = request.data.get('email')
        if not email:
            return Response(
                {'detail': 'Email is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{user.id}/{token}"
            
            print(f"Generated reset URL: {reset_url}")  # Debug print
            
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=[email],
                subject="Password Reset Request - Gift Sync",
                html_content=f'''
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2 style="color: #2c3e50; margin-bottom: 20px;">Password Reset Request</h2>
                        <p style="color: #34495e; line-height: 1.5;">
                            You have requested to reset your password. Click the link below to proceed:
                        </p>
                        <p style="margin: 25px 0;">
                            <a href="{reset_url}" style="background-color: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 3px;">
                                Reset Password
                            </a>
                        </p>
                        <p style="color: #34495e; line-height: 1.5;">
                            If you did not request this password reset, please ignore this email.
                        </p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                            Best regards,<br>
                            The Gift Sync Team
                        </p>
                    </div>
                '''
            )
            
            try:
                print("\nAttempting to send reset email...")
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                response = sg.send(message)
                
                print("\nResponse Details:")
                print(f"Status code: {response.status_code}")
                print(f"Headers: {response.headers}")
                
                if response.status_code == 202:
                    print("\nReset email sent successfully!")
                    return Response({'detail': 'Password reset email sent if account exists.'})
                else:
                    print(f"\nUnexpected status code: {response.status_code}")
                    return Response(
                        {'detail': 'Failed to send reset email. Please try again later.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                print("\nError Details:")
                print(f"Error type: {type(e)}")
                print(f"Error message: {str(e)}")
                if hasattr(e, 'body'):
                    print(f"Error body: {e.body.decode() if isinstance(e.body, bytes) else e.body}")
                if hasattr(e, 'headers'):
                    print(f"Error headers: {e.headers}")
                
                return Response(
                    {'detail': 'Failed to send reset email. Please try again later.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except User.DoesNotExist:
            print(f"\nNo user found with email: {email}")
            # For security, use the same message as success case
            return Response({'detail': 'Password reset email sent if account exists.'}) 

    @action(detail=False, methods=['POST'])
    def reset_password(self, request):
        print("\n=== Starting Password Reset Confirmation ===")
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        print(f"Processing reset confirmation for user_id: {user_id}")
        
        # Validate input
        if not all([user_id, token, new_password]):
            return Response(
                {'detail': 'Missing required fields.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            
            # Verify token
            if not default_token_generator.check_token(user, token):
                print(f"Invalid or expired token for user_id: {user_id}")
                return Response(
                    {'detail': 'Invalid or expired reset link.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            print(f"Successfully reset password for user_id: {user_id}")
            return Response({'detail': 'Password successfully reset.'})
            
        except User.DoesNotExist:
            print(f"No user found with id: {user_id}")
            return Response(
                {'detail': 'Invalid reset link.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"Unexpected error during password reset: {str(e)}")
            return Response(
                {'detail': 'An error occurred while resetting password.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([AllowAny])
def test_email(request):
    print("\n=== Starting Test Email ===")
    api_key = os.getenv('SENDGRID_API_KEY')
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    
    if not api_key:
        return Response({
            'status': 'error',
            'message': 'SendGrid API key not found'
        }, status=500)

    message = Mail(
        from_email="Gift Sync <crwilson311@gmail.com>",
        to_emails="crwilson311@gmail.com",
        subject="Test Email from Gift Sync",
        html_content='''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50; margin-bottom: 20px;">Test Email from Gift Sync</h2>
                <p style="color: #34495e; line-height: 1.5;">
                    This is a test email to verify your email configuration is working correctly.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #7f8c8d; font-size: 12px; text-align: center;">
                    Best regards,<br>
                    The Gift Sync Team
                </p>
            </div>
        '''
    )
    
    try:
        print("\nAttempting to send email...")
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        print("\nResponse Details:")
        print(f"Status code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Body: {response.body}")
        
        if response.status_code == 202:
            print("\nEmail sent successfully!")
            return Response({
                'status': 'success',
                'message': 'Test email sent successfully',
                'status_code': response.status_code
            })
        else:
            print(f"\nUnexpected status code: {response.status_code}")
            return Response({
                'status': 'error',
                'message': f'Unexpected status code: {response.status_code}'
            }, status=500)
            
    except Exception as e:
        print("\nError Details:")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        if hasattr(e, 'body'):
            print(f"Error body: {e.body.decode() if isinstance(e.body, bytes) else e.body}")
        if hasattr(e, 'headers'):
            print(f"Error headers: {e.headers}")
        
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# TEMPORARY ENDPOINT - Remove after running migration once
@api_view(['POST'])
@permission_classes([AllowAny])
def trigger_image_migration(request):
    """
    Temporary endpoint to trigger image migration on Railway.
    SECURITY: Remove this endpoint after running the migration!
    """
    from django.core.management import call_command
    from io import StringIO

    # Only allow in production (Railway)
    if not os.getenv('RAILWAY_ENVIRONMENT'):
        return Response({
            'status': 'error',
            'message': 'This endpoint only works on Railway'
        }, status=403)

    try:
        out = StringIO()
        err = StringIO()

        # Run the migration command
        call_command('download_wishlist_images', '--rescrape', stdout=out, stderr=err)

        return Response({
            'status': 'success',
            'output': out.getvalue(),
            'errors': err.getvalue() if err.getvalue() else None
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)