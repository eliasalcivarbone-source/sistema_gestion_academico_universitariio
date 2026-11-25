from django.urls import path

from . import views

app_name = "academico"

urlpatterns = [
    
    path("", views.InicioView.as_view(), name="inicio"),
    path("inicio/", views.InicioView.as_view(), name="inicio_alias"),
    path("estudiantes/", views.EstudianteCreateView.as_view(), name="estudiantes"),
    path("catalogo/", views.CatalogoView.as_view(), name="catalogo"),
    path("matriculas/", views.MatriculaCreateView.as_view(), name="matriculas"),
   path("matriculas/<int:pk>/eliminar/", views.MatriculaDeleteView.as_view(), name="matricula_eliminar"),
   path("matriculas/<int:pk>/notas/", views.MatriculaNotaUpdateView.as_view(), name="matricula_notas"),
   
   
#universidad
# Universidad
    path("universidades/", views.UniversidadListView.as_view(), name="universidad_lista"),
    path("universidades/crear/", views.UniversidadCreateView.as_view(), name="universidad_crear"),
    path("universidades/<int:pk>/", views.UniversidadDetailView.as_view(), name="universidad_detalle"),
    path("universidades/<int:pk>/editar/", views.UniversidadUpdateView.as_view(), name="universidad_editar"),
    path("universidades/<int:pk>/eliminar/", views.UniversidadDeleteView.as_view(), name="universidad_eliminar"),
    path("universidades/<int:pk>/pdf/", views.UniversidadPdfView.as_view(), name="universidad_pdf"),
]
   




