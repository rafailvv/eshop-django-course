import json

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.db.models import F, QuerySet, Value
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from django.http.response import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from shop.models import Product
from shop.forms import CustomUserCreationForm, UserAuthForm
from shop.mixins import IsAuthenticatedMixin

from django.http import HttpResponse
from .models import Product


def all_products(request):
    # Получаем все объекты модели Product
    products = Product.objects.all()

    # Формируем HTML-страницу как строку
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Список продуктов</title>
    </head>
    <body>
        <h1>Список продуктов</h1>
        <ul>
    """

    # Если есть продукты, формируем список
    if products.exists():
        for product in products:
            html += f"<li><strong>{product.name}</strong>"
            if getattr(product, 'description', None):
                html += f" – {product.description}"
            if getattr(product, 'price', None):
                html += f" – Цена: {product.price}"
            html += "</li>"
    else:
        html += "<li>Продукты отсутствуют</li>"

    # Завершаем HTML-страницу
    html += """
        </ul>
    </body>
    </html>
    """

    return HttpResponse(html)


class MainView(IsAuthenticatedMixin, ListView):
    template_name = 'index.html'
    model = Product
    context_object_name = 'products'
    ordering = ['-title']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related("productimage_set")


def register_page(request: HttpRequest):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("main-page")

    form = CustomUserCreationForm()
    return render(
        request,
        "registration.html",
        context={"form": form}
    )


class LoginView(View):
    @staticmethod
    def get(request: HttpRequest):
        form = UserAuthForm()
        return render(request, "login.html", context={"form": form})

    @staticmethod
    def post(request: HttpRequest):
        form = UserAuthForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("main-page")
            else:
                messages.error(request, "Неверное имя пользователя или пароль")
        else:
            messages.error(request, form.errors)

        form = UserAuthForm()
        return render(request, "login.html", context={"form": form})


def logout_page(request: HttpRequest):
    logout(request)
    return redirect("main-page")


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ProductDetailView(IsAuthenticatedMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        qs: QuerySet[Product] = super().get_queryset()
        if self.request.discount:
            discount = 500
            qs = qs.annotate(discount_price=F('price') - Value(discount))
        return qs.prefetch_related("productimage_set")

    def get_context_data(self, **kwargs):
        cd = super().get_context_data(**kwargs)
        cd["discount"] = self.request.discount
        return cd


class CartView(View):
    @staticmethod
    def get(request: HttpRequest, product_id: int):
        print(f"{request.discount=}")
        cart = request.session.get("cart")

        if cart is None:
            return JsonResponse({"detail": "Cart doesn't exists."}, status=404)

        if str(product_id) not in cart:
            return JsonResponse({"detail": "Product not in cart."}, status=404)

        return JsonResponse({"quantity": cart[str(product_id)]}, status=200)

    @staticmethod
    def post(request: HttpRequest):
        """

        {
            "productId": 1,
            "quantity": 2,
        }

        :param request:
        :return:
        """

        data = json.loads(request.body.decode('utf-8'))

        product_id = data["productId"]
        quantity = data["quantity"]

        cart = request.session.get("cart")

        if cart is None:
            cart = {}

        if str(product_id) not in cart:
            cart[str(product_id)] = quantity
        else:
            cart[str(product_id)] += quantity

        request.session.update({"cart": cart})

        return JsonResponse({"success": True})

    @staticmethod
    def delete(request: HttpRequest, product_id: int):
        cart = request.session.get("cart")

        if cart is None:
            return JsonResponse({"detail": "Cart doesn't exists."}, status=404)

        if str(product_id) not in cart:
            return JsonResponse({"detail": "Product not in cart."}, status=404)

        del cart[str(product_id)]
        request.session.update({"cart": cart})
        return JsonResponse({}, status=204)


class ShowCartView(View):
    @staticmethod
    def get(request: HttpRequest):
        """
        {
            <Product>: [quantity, total_price]
        }

        :param request:
        :return:
        """

        cart = request.session.get("cart")

        if cart is None:
            return JsonResponse({"detail": "Cart doesn't exists."}, status=404)

        products_ids = cart.keys()

        discount = 500
        products = Product.objects.filter(id__in=products_ids).annotate(
            discount_price=F('price') - Value(discount)
        )

        if request.discount:
            product_quantity_cart = {
                product: (cart.get(str(product.id)), cart.get(str(product.id)) * product.discount_price)
                for product in products
            }
        else:
            product_quantity_cart = {
                product: (cart.get(str(product.id)), cart.get(str(product.id)) * product.price)
                for product in products
            }

        return render(
            request,
            "cart.html",
            context={"cart": product_quantity_cart, "discount": request.discount}
        )


