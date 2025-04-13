from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DonorProfile, RequesterProfile

class DonorProfileInline(admin.StackedInline):
    model = DonorProfile
    can_delete = False
    verbose_name_plural = 'Donor Profile'
    fk_name = 'user'

class RequesterProfileInline(admin.StackedInline):
    model = RequesterProfile
    can_delete = False
    verbose_name_plural = 'Requester Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    inlines = [DonorProfileInline, RequesterProfileInline]
    
    def get_user_type(self, obj):
        return obj.get_user_type_display()
    get_user_type.short_description = 'User Type'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        inline_instances = []
        for inline_class in self.inlines:
            # Add only relevant profile inline based on user type
            if obj.user_type == User.DONOR and isinstance(inline_class, DonorProfileInline):
                inline = inline_class(self.model, self.admin_site)
                inline_instances.append(inline)
            elif obj.user_type == User.REQUESTER and isinstance(inline_class, RequesterProfileInline):
                inline = inline_class(self.model, self.admin_site)
                inline_instances.append(inline)
        return inline_instances

admin.site.register(User, CustomUserAdmin)
admin.site.register(DonorProfile)
admin.site.register(RequesterProfile)
