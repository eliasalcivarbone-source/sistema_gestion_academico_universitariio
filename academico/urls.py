from django.urls import path

from . import views

app_name = "academico"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("inicio/", views.inicio, name="inicio_alias"),
    path("estudiantes/", views.estudiantes, name="estudiantes"),
    path("catalogo/", views.catalogo , name="catalogo"),
]