from django.template.loader import render_to_string
from django.utils.html import format_html

from djangocms_versioning.constants import DRAFT

from djangocms_versioning.admin import VersioningAdminMixin
from djangocms_version_locking.helpers import version_is_locked


class VersionLockAdminMixin(VersioningAdminMixin):
    """
    Mixin providing versioning functionality to admin classes of
    version models.
    """

    def get_list_display(self, request):
        return (
            "get_name",
            "nr",
        )

    def get_name(self, request, obj):
        return format_html(
            "{lock}{name}",
            lock=self.is_locked(obj),
            name=getattr(obj, "name", obj.__str__)
        )

    def is_locked(self, obj):
        version = self.get_version(obj)
        if version.state == DRAFT and version_is_locked(version):
            return render_to_string("djangocms_version_locking/admin/locked_icon.html")
        return ""

    def has_change_permission(self, request, obj=None):
        """
        If there’s a lock for edited object and if that lock belongs
        to the current user
        """
        from .helpers import content_is_unlocked_for_user

        # User has permissions?
        has_permission = super().has_change_permission(request, obj)
        if not has_permission:
            return False

        # Check if the lock exists and belongs to the user
        if obj:
            return content_is_unlocked_for_user(obj, request.user)
        return True
