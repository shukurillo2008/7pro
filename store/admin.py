from django.contrib import admin

from .models import Category, Product, ProductImage, DescriptionSection, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class DescriptionSectionInline(admin.TabularInline):
    model = DescriptionSection
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['author', 'rating', 'content', 'created_at']
    can_delete = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'price', 'stock_status', 'is_featured', 'is_new', 'is_bestseller']
    list_filter = ['category', 'stock_status', 'is_featured', 'is_new', 'is_bestseller']
    search_fields = ['name', 'sku', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock_status', 'is_featured', 'is_new', 'is_bestseller']
    inlines = [ProductImageInline, DescriptionSectionInline, ReviewInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'sku', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Description', {
            'fields': ('short_description', 'specs')
        }),
        ('Status', {
            'fields': ('stock_status', 'is_featured', 'is_new', 'is_bestseller')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'is_primary', 'order']
    list_filter = ['product', 'is_primary']


@admin.register(DescriptionSection)
class DescriptionSectionAdmin(admin.ModelAdmin):
    list_display = ['product', 'title', 'order']
    list_filter = ['product']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'author', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['author', 'content']


from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone_number', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'phone_number', 'address', 'id']
    list_editable = ['status']
    inlines = [OrderItemInline]

