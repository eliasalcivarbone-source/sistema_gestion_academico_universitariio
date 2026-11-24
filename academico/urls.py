from django.urls import path

from . import views

app_name = "academico"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("inicio/", views.inicio, name="inicio_alias"),
    path("estudiantes/", views.estudiantes, name="estudiantes"),
    path("catalogo/", views.catalogo , name="catalogo"),
    path("matriculas/", views.MatriculaCreateView.as_view(), name="matriculas"),
   path("matriculas/<int:pk>/eliminar/", views.MatriculaDeleteView.as_view(), name="matricula_eliminar"),
]