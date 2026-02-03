from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Category, Product


def home(request):
    """Homepage with featured products and categories"""
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)[:3]
    new_products = Product.objects.filter(is_new=True)[:6]
    
    from core.models import HomeSettings, Feature
    
    # Homepage Data
    home_settings = HomeSettings.objects.first()
    features = Feature.objects.all()
    
    # Stats (use from DB or fallback)
    if home_settings:
        stats = {
            'parts_shipped': home_settings.parts_shipped,
            'tournaments_won': home_settings.tournaments_won,
        }
    else:
         stats = {
            'parts_shipped': '2.4k+',
            'tournaments_won': '150+',
        }
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_products': new_products,
        'stats': stats,
        'home_settings': home_settings,
        'features': features,
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


def _cart_id(request):
    """Helper to get or create cart ID (session key)"""
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    """Add item to cart"""
    from .models import Cart, CartItem
    from django.shortcuts import redirect

    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        # If item exists, increment quantity
        # (Assuming we might want to increment by 1 each click, or based on form input.
        # For simple 'add to cart' often implies +1 or set to qty. 
        # The frontend detail page has a quantity input, so we should try to get that.)
        
        if request.method == 'POST':
             # If coming from a form with quantity
             qty = int(request.POST.get('quantity', 1))
             cart_item.quantity += qty
        else:
             cart_item.quantity += 1
        
        cart_item.save()
    except CartItem.DoesNotExist:
        qty = 1
        if request.method == 'POST':
            qty = int(request.POST.get('quantity', 1))
            
        cart_item = CartItem.objects.create(
            product=product,
            quantity=qty,
            cart=cart
        )
        cart_item.save()
    
    cart_item.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Calculate new cart count
        cart_count = 0
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            cart_count += item.quantity
            
        return JsonResponse({
            'success': True,
            'message': 'Added to cart successfully!',
            'cart_count': cart_count,
            'product_name': product.name
        })
    
    return redirect('cart')


def remove_cart(request, product_id):
    """Decrement item quantity or remove if 1"""
    from .models import Cart, CartItem
    from django.shortcuts import redirect

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request, product_id):
    """Remove item completely from cart"""
    from .models import Cart, CartItem
    from django.shortcuts import redirect

    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    """Cart page view"""
    from .models import Cart, CartItem
    from django.core.exceptions import ObjectDoesNotExist
    
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        # Simple tax calculation (e.g. 2%) - Optional
        # tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass # Just empty cart

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)


def checkout(request, total=0, quantity=0, cart_items=None):
    """Checkout page and logic"""
    from .models import Cart, CartItem, Order, OrderItem
    from django.core.exceptions import ObjectDoesNotExist
    from django.shortcuts import redirect

    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        grand_total = total + tax
    except ObjectDoesNotExist:
        return redirect('shop') # Empty cart, go back to shop

    if request.method == 'POST':
        # Create Order
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        location = request.POST.get('location', '')
        
        # Basic validation
        if not (full_name and phone_number and address):
             # Ideally return with error message
             pass

        order = Order.objects.create(
            full_name=full_name,
            phone_number=phone_number,
            address=address,
            location=location,
            status='New'
        )
        order.save()

        # Move Cart Items to Order Items
        for item in cart_items:
            order_item = OrderItem()
            order_item.order = order
            order_item.product = item.product
            order_item.price = item.product.price
            order_item.quantity = item.quantity
            order_item.save()
            
            # Reduce stock? (Not strictly implemented yet, but keeping note)
            # product = Product.objects.get(id=item.product.id)
            # product.stock -= item.quantity
            # product.save()

        # Clear Cart
        cart_items.delete()
        cart.delete()

        # Redirect to a success page or back home with message
        # For now, let's redirect to home
        return redirect('home')

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'checkout.html', context)

