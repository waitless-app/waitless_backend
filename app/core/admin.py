from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .forms import GroupAdminForm
from django.contrib.auth.models import Group
from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


class OrderAdmin(admin.ModelAdmin):
    fields = (
        'status', 'customer', 'premises', 'order_comment'
    )
    list_display = (
        'id', 'status', 'created', 'updated'
    )
    list_filter = (
        'status',
    )
    readonly_fieldset = (
        'id', 'created', 'updated',
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Premises)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderProduct)
admin.site.register(models.Product)
admin.site.register(models.Menu)
admin.site.register(models.ProductCategory)
admin.site.unregister(Group)

# Create a new Group admin.


class GroupAdmin(admin.ModelAdmin):
    # Use our custom form.
    form = GroupAdminForm
    # Filter permissions horizontal as well.
    filter_horizontal = ['permissions']


# Register the new Group ModelAdmin.
admin.site.register(Group, GroupAdmin)
