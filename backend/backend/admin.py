from django.contrib.admin.models import LogEntry
from django.contrib.admin.utils import quote
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils.html import format_html

class CustomLogEntry(LogEntry):
    class Meta:
        proxy = True

    def get_edited_object(self):
        """Returns the edited object represented by this log entry"""
        return self.content_type.get_object_for_this_type(pk=self.object_id)

    def get_admin_url(self):
        """
        Returns the admin URL to edit the object represented by this log entry.
        """
        if self.content_type and self.object_id:
            url_name = f'admin:{self.content_type.app_label}_{self.content_type.model}_change'
            return reverse(url_name, args=[quote(self.object_id)])

class CustomLogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'filtered_object_repr', 'action_flag', 'change_message']
    list_filter = ['action_time', 'user', 'content_type']
    search_fields = ['object_repr', 'change_message']
    date_hierarchy = 'action_time'

    def filtered_object_repr(self, obj):
        """Filter out purchased information if viewer is the wishlist owner"""
        if obj.content_type.model == 'wishlistitem':
            item = obj.get_edited_object()
            if item and self.request.user == item.wishlist.owner:
                return "Wishlist Item Updated"
            return obj.object_repr
        return obj.object_repr
    filtered_object_repr.short_description = 'Object'

# Unregister the default LogEntry
admin.site.unregister(LogEntry)
# Register our custom LogEntry
admin.site.register(CustomLogEntry, CustomLogEntryAdmin) 