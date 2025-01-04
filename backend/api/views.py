class WishlistItemViewSet(viewsets.ModelViewSet):
    # ... existing code ...

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # If user is viewing their own wishlist items, exclude purchased information
        if 'wishlist' in self.request.query_params:
            wishlist_id = self.request.query_params['wishlist']
            wishlist = Wishlist.objects.get(id=wishlist_id)
            if wishlist.owner == user:
                # Use defer to exclude purchased-related fields from the query
                queryset = queryset.defer('purchased', 'purchased_by', 'purchased_date')
        
        return queryset

    def perform_update(self, serializer):
        instance = self.get_object()
        # Prevent wishlist owners from updating purchased information
        if instance.wishlist.owner == self.request.user:
            if 'purchased' in serializer.validated_data:
                serializer.validated_data.pop('purchased')
            if 'purchased_by' in serializer.validated_data:
                serializer.validated_data.pop('purchased_by')
            if 'purchased_date' in serializer.validated_data:
                serializer.validated_data.pop('purchased_date')
        
        serializer.save() 