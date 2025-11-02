"""
Admin configuration for the SÎKÂ e-commerce platform.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    User, Product, Category, Tag, Cart, CartItem, Order,
    OrderItem, SellerRequest, ProductImage, Wishlist, ProductReview
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """User admin interface."""
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'is_seller', 'is_email_verified', 'date_joined'
    ]
    list_filter = [
        'is_seller', 'is_email_verified', 'is_staff', 'is_active'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login']
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('username', 'email', 'first_name', 'last_name',
                       'phone', 'address')
        }),
        ('Statut', {
            'fields': ('is_seller', 'is_seller_approved', 'is_email_verified',
                       'is_active', 'is_staff', 'is_superuser')
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Dates', {
            'fields': ('date_joined', 'last_login'),
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin interface."""
    list_display = ['name', 'slug', 'product_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        """Count products in category."""
        return obj.products.count()
    product_count.short_description = 'Nombre de produits'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag admin interface."""
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SellerRequest)
class SellerRequestAdmin(admin.ModelAdmin):
    """Seller request admin interface."""
    list_display = [
        'user', 'store_name', 'status', 'phone', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'store_name', 'store_name']
    readonly_fields = ['user', 'created_at', 'reviewed_at']
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        """Approve selected seller requests."""
        for seller_request in queryset:
            seller_request.status = 'approved'
            seller_request.reviewed_at = timezone.now()
            seller_request.user.is_seller = True
            seller_request.user.save()
            seller_request.save()
        self.message_user(
            request,
            f'{queryset.count()} demande(s) approuvée(s) avec succès.'
        )
    approve_requests.short_description = 'Approuver les demandes sélectionnées'

    def reject_requests(self, request, queryset):
        """Reject selected seller requests."""
        for seller_request in queryset:
            seller_request.status = 'rejected'
            seller_request.reviewed_at = timezone.now()
            seller_request.save()
        self.message_user(
            request,
            f'{queryset.count()} demande(s) rejetée(s).'
        )
    reject_requests.short_description = 'Rejeter les demandes sélectionnées'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product admin interface."""
    list_display = [
        'name', 'seller', 'price', 'stock', 'category',
        'is_active', 'created_at'
    ]
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'description', 'seller__username']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['seller', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'description', 'price')
        }),
        ('Visuels', {
            'fields': ('image', 'category')
        }),
        ('Mots-clés', {
            'fields': ('tags',)
        }),
        ('Stock', {
            'fields': ('stock', 'is_active')
        }),
        ('Vendeur', {
            'fields': ('seller',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


class OrderItemInline(admin.TabularInline):
    """Order item inline admin."""
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']
    fk_name = 'order'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin interface."""
    list_display = [
        'order_number', 'user', 'status', 'total_amount',
        'payment_method', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__username']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Informations de commande', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('Livraison', {
            'fields': ('delivery_address', 'phone')
        }),
        ('Paiement', {
            'fields': ('payment_method', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Cart admin interface."""
    list_display = ['user', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_total(self, obj):
        """Get total for cart."""
        return obj.get_total()
    get_total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Cart item admin interface."""
    list_display = ['cart', 'product', 'quantity', 'total_price']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

    def total_price(self, obj):
        """Display total price for cart item."""
        return f'{obj.get_total():.0f} FCFA'
    total_price.short_description = 'Total'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Product image admin interface."""
    list_display = ['product', 'image', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Wishlist admin interface."""
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['created_at']


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Product review admin interface."""
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['rating']