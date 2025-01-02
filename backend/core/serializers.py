from rest_framework import serializers
from .models import User, Family, WishList, WishListItem, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile_picture', 'bio')
        read_only_fields = ('id',)

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
    class Meta:
        model = WishListItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

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