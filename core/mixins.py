from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import ProtectedError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

from .utils import exportar_excel, render_pdf, valor_campo


class UsuarioRegistroMixin:
    """Asigna automáticamente el usuario autenticado al registrar o editar."""

    def form_valid(self, form):
        if self.request.user.is_authenticated and hasattr(form.instance, "user"):
            form.instance.user = self.request.user
        return super().form_valid(form)


class FiltroCamposMixin:
    """Filtros GET y selección dinámica de columnas para ListView."""

    filtro_form_class = None
    campos_disponibles = []
    campos_por_defecto = []

    def filtrar(self, queryset, datos):
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filtro_form = (
            self.filtro_form_class(self.request.GET or None)
            if self.filtro_form_class
            else None
        )
        if self.filtro_form is not None and self.filtro_form.is_valid():
            queryset = self.filtrar(queryset, self.filtro_form.cleaned_data)
        return queryset

    def get_campos_seleccionados(self):
        titulos = dict(self.campos_disponibles)
        elegidos = [c for c in self.request.GET.getlist("campos") if c in titulos]
        elegidos = elegidos or self.campos_por_defecto or list(titulos)
        return [(c, titulos[c]) for c in elegidos]

    def filtros_aplicados(self):
        resumen = []
        if not getattr(self, "filtro_form", None) or not self.filtro_form.is_valid():
            return resumen
        for nombre, valor in self.filtro_form.cleaned_data.items():
            if valor in (None, "", [], ()):
                continue
            etiqueta = self.filtro_form.fields[nombre].label or nombre
            if hasattr(valor, "__iter__") and not isinstance(valor, (str, bytes)):
                texto_val = ", ".join(str(v) for v in valor)
            else:
                texto_val = str(valor)
            resumen.append(f"{etiqueta}: {texto_val}")
        return resumen

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        campos = self.get_campos_seleccionados()
        contexto["filtro_form"] = self.filtro_form
        contexto["campos_disponibles"] = self.campos_disponibles
        contexto["campos_seleccionados"] = [c for c, _ in campos]
        contexto["encabezados"] = [t for _, t in campos]
        contexto["filas"] = [
            (obj, [valor_campo(obj, c) for c, _ in campos])
            for obj in contexto["object_list"]
        ]
        consulta = self.request.GET.copy()
        consulta.pop("page", None)
        consulta.pop("exportar", None)
        contexto["consulta"] = consulta.urlencode()
        return contexto


class ExportarMixin(FiltroCamposMixin):
    """Exporta el queryset filtrado (sin paginar) a Excel o PDF."""

    titulo_reporte = "Reporte"
    nombre_archivo = "reporte"
    template_pdf_listado = "core/pdf/listado.html"

    def get(self, request, *args, **kwargs):
        formato = request.GET.get("exportar")
        if formato not in ("excel", "pdf"):
            return super().get(request, *args, **kwargs)

        queryset = self.get_queryset()
        campos = self.get_campos_seleccionados()
        encabezados = [t for _, t in campos]
        filas = [[valor_campo(obj, c) for c, _ in campos] for obj in queryset]

        if formato == "excel":
            return exportar_excel(
                self.titulo_reporte,
                encabezados,
                filas,
                self.nombre_archivo,
            )

        contexto = {
            "titulo": self.titulo_reporte,
            "encabezados": encabezados,
            "filas": filas,
            "total": len(filas),
            "filtros": self.filtros_aplicados(),
            "fecha": timezone.localtime(),
            "usuario": request.user,
        }
        return render_pdf(
            self.template_pdf_listado,
            contexto,
            self.nombre_archivo,
        )


class ComprobantePdfMixin:
    """Convierte una DetailView en un comprobante PDF."""

    template_pdf = None
    nombre_archivo = "comprobante"

    def render_to_response(self, context, **response_kwargs):
        context["fecha"] = timezone.localtime()
        context["usuario"] = self.request.user
        pk = getattr(self.object, "pk", "detalle")
        return render_pdf(
            self.template_pdf,
            context,
            f"{self.nombre_archivo}-{pk}",
        )


class EliminarProtegidoMixin:
    """Atrapa ProtectedError al eliminar un registro con hijos relacionados."""

    mensaje_protegido = "No se puede eliminar porque tiene registros asociados."
    url_error = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, self.mensaje_protegido)
            destino = self.url_error or self.success_url
            return redirect(destino)