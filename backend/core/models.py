from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils.image_downloader import download_image_from_url, ImageDownloadException
import logging

logger = logging.getLogger(__name__)

class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Family(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='families')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Families'
    
    def __str__(self):
        return self.name

class WishList(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.owner.username}'s {self.name}"

class WishListItem(models.Model):
    SIZES = [
        ('Stocking', 'Stocking'),  # $0-25
        ('Small', 'Small'),        # $26-50
        ('Medium', 'Medium'),      # $51-100
        ('Large', 'Large'),        # $100+
    ]
    
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    link = models.URLField(blank=True, max_length=2000)
    image = models.ImageField(upload_to='wishlist_items/', blank=True, null=True)
    image_url = models.URLField(blank=True, max_length=1000)
    size = models.CharField(max_length=10, choices=SIZES, default='Medium')
    priority = models.IntegerField(default=3)
    is_purchased = models.BooleanField(default=False)
    purchased_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchased_items')
    purchased_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Download image from URL if image_url is provided and no image file exists
        if self.image_url and not self.image:
            try:
                logger.info(f"Downloading image from URL: {self.image_url}")
                result = download_image_from_url(self.image_url)
                if result:
                    content_file, filename = result
                    self.image.save(filename, content_file, save=False)
                    # Clear image_url after successful download
                    self.image_url = ''
                    logger.info(f"Successfully saved image as: {filename}")
            except ImageDownloadException as e:
                logger.error(f"Failed to download image from {self.image_url}: {str(e)}")
                # Keep the image_url if download fails, but continue saving the model
            except Exception as e:
                logger.error(f"Unexpected error downloading image: {str(e)}")
                # Keep the image_url if download fails, but continue saving the model

        # Clear image_url if uploading a new image file
        elif self.image and self.image_url:
            self.image_url = ''

        # Size logic...
        if self.price is not None:
            if self.price <= 25:
                self.size = 'Stocking'
            elif self.price <= 50:
                self.size = 'Small'
            elif self.price <= 100:
                self.size = 'Medium'
            else:
                self.size = 'Large'
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['priority', '-created_at']

class Notification(models.Model):
    TYPES = [
        ('new_item', 'New Item Added'),
        ('purchased', 'Item Purchased'),
        ('wishlist_created', 'Wishlist Created'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPES)
    target_id = models.IntegerField()  # ID of the related object (wishlist or item)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at'] 