# compradoresApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages

from .models import Favorite, Order, Review, Notification
from .forms import CompradorLoginForm, ReviewForm, FilterForm

# IMPORTACIÓN CORRECTA desde proyectoApp
from proyectoApp.models import Producto


# --------------------------
# LOGIN / LOGOUT
# --------------------------
def comprador_login(request):
    if request.method == "POST":
        form = CompradorLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next') or reverse('compradores:catalog'))
    else:
        form = CompradorLoginForm(request)

    return render(request, 'compradoresApp/login.html', {'form': form})


def comprador_logout(request):
    logout(request)
    return redirect('compradores:login')


# --------------------------
# CATÁLOGO
# --------------------------
def catalog(request):
    qs = Producto.objects.all().order_by("-fecha_creacion")
    form = FilterForm(request.GET)

    if form.is_valid():
        category = form.cleaned_data.get("category")
        location = form.cleaned_data.get("location")
        min_price = form.cleaned_data.get("min_price")
        max_price = form.cleaned_data.get("max_price")

        if category:
            qs = qs.filter(categoria__icontains=category)
        if location:
            qs = qs.filter(tienda__ubicacion__icontains=location)
        if min_price:
            qs = qs.filter(precio__gte=min_price)
        if max_price:
            qs = qs.filter(precio__lte=max_price)

    if request.user.is_authenticated:
        for p in qs:
            p.is_favorite = Favorite.objects.filter(user=request.user, product=p).exists()
    else:
        for p in qs:
            p.is_favorite = False

    paginator = Paginator(qs, 12)
    page = request.GET.get('page')
    productos = paginator.get_page(page)

    return render(request, 'compradoresApp/catalog.html', {
        'products': productos,
        'form': form
    })


# --------------------------
# DETALLE DE PRODUCTO
# --------------------------
def product_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    review_form = ReviewForm()

    is_fav = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, product=producto).exists()

    reviews = Review.objects.filter(product=producto, active=True).order_by('-created_at')

    return render(request, 'compradoresApp/product_detail.html', {
        'product': producto,
        'reviews': reviews,
        'review_form': review_form,
        'is_fav': is_fav
    })


# --------------------------
# AGREGAR REVIEW
# --------------------------
@login_required
def add_review(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.product = producto
            rev.author = request.user
            rev.save()

            # Notificar al ARTESANO REAL
            Notification.objects.create(
                user=producto.tienda.artesano.user,
                message=f"Tu producto '{producto.nombre}' recibió una nueva reseña."
            )

            messages.success(request, "Reseña agregada exitosamente.")

    return redirect('compradores:product_detail', pk=producto.pk)


# --------------------------
# TOGGLE FAVORITOS
# --------------------------
@login_required
def toggle_favorite(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    fav, created = Favorite.objects.get_or_create(
        user=request.user,
        product=producto
    )

    if not created:
        fav.delete()
        messages.info(request, "Eliminado de favoritos.")
    else:
        messages.success(request, "Agregado a favoritos.")

    return redirect(request.META.get('HTTP_REFERER', 'compradores:catalog'))


# --------------------------
# LISTA DE FAVORITOS
# --------------------------
@login_required
def favorites_list(request):
    favs = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'compradoresApp/favorites.html', {'favs': favs})


# --------------------------
# NOTIFICACIONES
# --------------------------
@login_required
def notifications_list(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'compradoresApp/notifications.html', {'notifications': notifs})


def returns_policy(request):
    return render(request, 'compradoresApp/returns_policy.html')


# --------------------------
# COMPRAR PRODUCTO
# --------------------------
@login_required
def create_order(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    order = Order.objects.create(
        buyer=request.user,
        product=producto,
        quantity=1,
        status='P'
    )

    Notification.objects.create(
        user=producto.tienda.artesano.user,
        message=f"Nuevo pedido de '{producto.nombre}' por {request.user.username}."
    )

    messages.success(request, "Compra realizada con éxito.")
    return redirect('compradores:product_detail', pk=pk)


# --------------------------
# OTRAS VISTAS
# --------------------------
def comprador_home(request):
    return render(request, 'compradoresApp/home.html')


def inicio_comprador(request):
    return render(request, "compradoresApp/inicio_comprador.html")
