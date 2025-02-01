"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from shop.views import (
    MainView,
    register_page,
    logout_page,
    LoginView,
    ProductDetailView,
    CartView,
    ShowCartView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name="main-page"),
    path('register/', register_page, name="register-page"),
    path("login/", LoginView.as_view(), name="login-page"),
    path("logout/", logout_page, name="logout"),
    path("products/<int:pk>", ProductDetailView.as_view(), name="product-detail"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/<int:product_id>", CartView.as_view(), name="cart"),
    path("showcart/", ShowCartView.as_view(), name="showcart"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
