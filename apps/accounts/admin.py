from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, OTP, EitaUser, TelegramUser, BaleUser


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "full_name",
        "mobile",
        "email",
        "user_type",
        "is_active",
        "is_staff",
        "last_login",
    )
    list_filter = (
        "user_type",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = ("username", "full_name", "mobile", "email", "uid")
    ordering = ("-date_joined",)
    readonly_fields = (
        "uid",
        "last_login",
        "date_joined",
        "created_at",
        "modified_at",
    )
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("full_name", "first_name", "last_name", "email", "mobile", "uid")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "user_type",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined", "created_at", "modified_at")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "mobile",
                    "email",
                    "full_name",
                    "user_type",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        "mobile",
        "code",
        "uuid",
        "created_at",
        "expires_at",
        "is_used",
        "is_verified",
    )
    list_filter = ("is_used", "is_verified")
    search_fields = ("mobile", "uuid", "code")
    readonly_fields = ("uuid",)
    ordering = ("-created_at",)


@admin.register(EitaUser)
class EitaUserAdmin(admin.ModelAdmin):
    list_display = ("uid", "created_at", "last_login_at")
    search_fields = ("uid",)
    readonly_fields = ("uid",)
    ordering = ("-created_at",)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("uid", "telegram_id", "mobile", "created_at", "last_login_at", "initial_message_sent")
    search_fields = ("uid", "telegram_id", "mobile")
    readonly_fields = ("uid",)
    ordering = ("-created_at",)


@admin.register(BaleUser)
class BaleUserAdmin(admin.ModelAdmin):
    list_display = ("uid", "bale_id", "mobile", "created_at", "last_login_at", "initial_message_sent")
    search_fields = ("uid", "bale_id", "mobile")
    readonly_fields = ("uid",)
    ordering = ("-created_at",)

