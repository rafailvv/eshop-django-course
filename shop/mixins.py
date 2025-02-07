from django.shortcuts import redirect
from django.urls import reverse_lazy

class IsAuthenticatedMixin:
    login_url = reverse_lazy('login')  # Убедитесь, что в urls.py определён URL с именем 'login'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)
