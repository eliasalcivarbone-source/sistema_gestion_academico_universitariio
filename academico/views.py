from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
)

from core.mixins import ComprobantePdfMixin, ExportarMixin, UsuarioRegistroMixin
from .forms import (
    CatalogoForm, EstudianteForm, MatriculaForm, NotaForm,
    FiltroUniversidadForm, UniversidadForm
)
from .models import Carrera, Estudiante, Matricula, Nota, Seccion, Universidad


# =====================================================================
# VISTAS BÁSICAS
# =====================================================================
class InicioView(LoginRequiredMixin, TemplateView):
    template_name = "academico/inicio.html"


class EstudianteCreateView(LoginRequiredMixin, CreateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = "academico/estudiantes.html"
    success_url = reverse_lazy("academico:catalogo")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estudiantes"] = Estudiante.objects.select_related("carrera").all()
        return context


class CatalogoView(LoginRequiredMixin, ListView):
    model = Seccion
    template_name = "academico/catalogo.html"
    context_object_name = "secciones"

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            "curso__carrera", "curso__semestre", "periodo", "profesor"
        )
        form = CatalogoForm(self.request.GET or None)
        if form.is_valid():
            carrera = form.cleaned_data.get("carrera")
            jornada = form.cleaned_data.get("jornada")
            if carrera:
                queryset = queryset.filter(curso__carrera=carrera)
            if jornada:
                queryset = queryset.filter(jornada=jornada)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CatalogoForm(self.request.GET or None)
        context["carreras"] = Carrera.objects.select_related("facultad").prefetch_related("cursos")
        return context


# =====================================================================
# MATRÍCULAS Y NOTAS
# =====================================================================
class MatriculaCreateView(LoginRequiredMixin, CreateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = "academico/matriculas.html"
    success_url = reverse_lazy("academico:matriculas")

    def form_valid(self, form):
        response = super().form_valid(form)
        Nota.objects.get_or_create(matricula=self.object)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matriculas"] = Matricula.objects.select_related(
            "estudiante__carrera", "seccion__curso", "seccion__periodo", "nota"
        ).all()
        return context


class MatriculaDeleteView(LoginRequiredMixin, DeleteView):
    model = Matricula
    template_name = "academico/matricula_confirm_delete.html"
    success_url = reverse_lazy("academico:matriculas")


class MatriculaNotaUpdateView(LoginRequiredMixin, View):
    template_name = "academico/Nota.html"
    success_url = reverse_lazy("academico:matriculas")

    def _get_matricula_y_nota(self, pk):
        matricula = get_object_or_404(Matricula, pk=pk)
        nota, _ = Nota.objects.get_or_create(matricula=matricula)
        return matricula, nota

    def get(self, request, pk):
        matricula, nota = self._get_matricula_y_nota(pk)
        form = NotaForm(instance=nota)
        return render(request, self.template_name, {"form": form, "matricula": matricula, "nota": nota})

    def post(self, request, pk):
        matricula, nota = self._get_matricula_y_nota(pk)
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        return render(request, self.template_name, {"form": form, "matricula": matricula, "nota": nota})


# =====================================================================
# CRUD DE UNIVERSIDAD
# =====================================================================
class UniversidadListView(LoginRequiredMixin, ExportarMixin, ListView):
    model = Universidad
    template_name = "academico/universidad_lista.html"
    context_object_name = "universidades"
    paginate_by = 10
    filtro_form_class = FiltroUniversidadForm
    campos_disponibles = [
        ("siglas", "Siglas"),
        ("nombre", "Nombre"),
        ("ciudad", "Ciudad"),
        ("total_facultades", "N.º de facultades"),
    ]
    campos_por_defecto = ["siglas", "nombre", "ciudad", "total_facultades"]
    titulo_reporte = "Listado de universidades"
    nombre_archivo = "universidades"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("facultades").order_by("nombre")

    def filtrar(self, queryset, datos):
        texto = (datos.get("texto") or "").strip()
        ciudad = (datos.get("ciudad") or "").strip()
        if texto:
            queryset = queryset.filter(Q(nombre__icontains=texto) | Q(siglas__icontains=texto))
        if ciudad:
            queryset = queryset.filter(ciudad__icontains=ciudad)
        return queryset


class UniversidadDetailView(LoginRequiredMixin, DetailView):
    model = Universidad
    template_name = "academico/universidad_detalle.html"
    context_object_name = "universidad"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["facultades"] = self.object.facultades.prefetch_related("carreras").order_by("nombre")
        return context


class UniversidadCreateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, CreateView):
    model = Universidad
    form_class = UniversidadForm
    template_name = "academico/universidad_form.html"
    success_url = reverse_lazy("academico:universidad_lista")
    success_message = "Universidad creada correctamente."


class UniversidadUpdateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, UpdateView):
    model = Universidad
    form_class = UniversidadForm
    template_name = "academico/universidad_form.html"
    success_url = reverse_lazy("academico:universidad_lista")
    success_message = "Universidad actualizada correctamente."


class UniversidadDeleteView(LoginRequiredMixin, DeleteView):
    model = Universidad
    template_name = "academico/universidad_eliminar.html"
    context_object_name = "universidad"
    success_url = reverse_lazy("academico:universidad_lista")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(request, "Universidad eliminada correctamente.")
            return response
        except ProtectedError:
            messages.error(request, "No se puede eliminar: tiene facultades asociadas.")
            return redirect("academico:universidad_lista")


class UniversidadPdfView(LoginRequiredMixin, ComprobantePdfMixin, DetailView):
    model = Universidad
    template_pdf = "academico/pdf/universidad_ficha.html"
    nombre_archivo = "universidad"
    context_object_name = "universidad"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["facultades"] = self.object.facultades.prefetch_related("carreras").order_by("nombre")
        return context
    
    
    

# =====================================================================
# CRUD DE ESTUDIANTES
# =====================================================================
class EstudianteListView(LoginRequiredMixin, ListView):
    model = Estudiante
    template_name = "academico/estudiante_lista.html"
    context_object_name = "estudiantes"
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().select_related("carrera").order_by("apellidos", "nombres")


class EstudianteDetailView(LoginRequiredMixin, DetailView):
    model = Estudiante
    template_name = "academico/estudiante_detalle.html"
    context_object_name = "estudiante"


class EstudianteCreateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, CreateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = "academico/estudiante_form.html"
    success_url = reverse_lazy("academico:estudiante_lista")
    success_message = "Estudiante creado correctamente."


class EstudianteUpdateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, UpdateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = "academico/estudiante_form.html"
    success_url = reverse_lazy("academico:estudiante_lista")
    success_message = "Estudiante actualizado correctamente."

from django.db.models import ProtectedError
from django.contrib import messages
from django.shortcuts import redirect

class EstudianteDeleteView(LoginRequiredMixin, DeleteView):
    model = Estudiante
    template_name = "academico/estudiante_eliminar.html"
    context_object_name = "estudiante"
    success_url = reverse_lazy("academico:estudiante_lista")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            response = super().post(request, *args, **kwargs)
            messages.success(request, "Estudiante eliminado correctamente.")
            return response
        except ProtectedError:
            messages.error(request, "No se puede eliminar: el estudiante ya tiene matrículas registradas.")
            return redirect("academico:estudiante_lista")

class EstudiantePdfView(LoginRequiredMixin, ComprobantePdfMixin, DetailView):
    model = Estudiante
    template_pdf = "academico/pdf/estudiante_ficha.html"
    nombre_archivo = "estudiante"
    context_object_name = "estudiante"