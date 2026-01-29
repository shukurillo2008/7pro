from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Category, Product


def home(request):
    """Homepage with featured products and categories"""
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)[:3]
    new_products = Product.objects.filter(is_new=True)[:6]
    
    # Stats for hero section
    stats = {
        'parts_shipped': '2.4k+',
        'tournaments_won': '150+',
    }
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
        'stats': stats,
    }
    return render(request, 'index.html', context)


def shop(request):
    """Product listing with filtering and pagination"""
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # Filter by category
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    # Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:  # featured
        products = products.order_by('-is_featured', '-is_bestseller', '-created_at')
    
    # Pagination
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'current_sort': sort,
        'total_count': paginator.count,
    }
    return render(request, 'shop.html', context)


def category_products(request, category_slug):
    """Products filtered by category"""
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category)
    categories = Category.objects.all()
    
    # Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-is_featured', '-is_bestseller', '-created_at')
    
    # Pagination
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'selected_category': category,
        'current_sort': sort,
        'total_count': paginator.count,
    }
    return render(request, 'shop.html', context)


def product_detail(request, slug):
    """Single product view with all details"""
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'description_sections', 'reviews'),
        slug=slug
    )
    
    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:3]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)
