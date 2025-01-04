class WishlistItemSerializer(serializers.ModelSerializer):
    # ... existing fields ...

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # If the viewer is the wishlist owner, hide purchased information
        if request and request.user == instance.wishlist.owner:
            data.pop('purchased', None)
            data.pop('purchased_by', None)
            data.pop('purchased_date', None)
        
        return data

    class Meta:
        model = WishlistItem
        fields = ['id', 'name', 'description', 'url', 'price', 'priority', 
                 'purchased', 'purchased_by', 'purchased_date', 'wishlist']
        read_only_fields = ['purchased', 'purchased_by', 'purchased_date'] 