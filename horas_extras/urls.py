# horas_extras/urls.py

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('calcular-he/', include('registros.urls')),
    path('', RedirectView.as_view(url='/calcular-he/')),
]