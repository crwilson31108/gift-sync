from rest_framework import serializers
from .models import User, Family, WishList, WishListItem, Notification

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'bio', 'full_name')
        read_only_fields = ('id',)

    def get_full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return obj.username  # Fallback to username if no name is set

class FamilySerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Family
        fields = ('id', 'name', 'members', 'member_ids', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        family = Family.objects.create(**validated_data)
        
        # Add the creator as a member
        request = self.context.get('request')
        if request and request.user:
            family.members.add(request.user)
        
        # Add other members
        if member_ids:
            members = User.objects.filter(id__in=member_ids)
            family.members.add(*members)
        
        return family

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('member_ids', None)
        
        # Update basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Update members if provided
        if member_ids is not None:
            # Keep the owner in the family
            owner = instance.members.filter(id=instance.members.first().id)
            instance.members.set(owner)
            # Add new members
            members = User.objects.filter(id__in=member_ids)
            instance.members.add(*members)
        
        return instance

class WishListItemSerializer(serializers.ModelSerializer):
    purchased_by = UserSerializer(read_only=True)
    
    class Meta:
        model = WishListItem
        fields = (
            'id', 'title', 'description', 'price', 'link', 
            'image', 'image_url', 'size', 'priority',
            'is_purchased', 'purchased_at', 'purchased_by',
            'created_at', 'updated_at', 'wishlist'
        )
        read_only_fields = (
            'id', 'created_at', 'updated_at', 
            'purchased_by', 'purchased_at'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # If the viewer is the wishlist owner, hide purchased information
        if request and request.user == instance.wishlist.owner:
            data.pop('is_purchased', None)
            data.pop('purchased_by', None)
            data.pop('purchased_at', None)
        
        return data

    def create(self, validated_data):
        # Ensure image_url is saved
        image_url = validated_data.get('image_url', '')
        instance = super().create(validated_data)
        if image_url:
            instance.image_url = image_url
            instance.save()
        return instance

    def update(self, instance, validated_data):
        # Ensure image_url is updated
        image_url = validated_data.get('image_url', instance.image_url)
        instance = super().update(instance, validated_data)
        if image_url:
            instance.image_url = image_url
            instance.save()
        return instance

class WishListSerializer(serializers.ModelSerializer):
    items = WishListItemSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = WishList
        fields = ('id', 'name', 'owner', 'family', 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'created_at') 