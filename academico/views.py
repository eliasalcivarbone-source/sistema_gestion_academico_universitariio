from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView

from .forms import CatalogoForm, EstudianteForm, MatriculaForm, NotaForm
from .models import Carrera, Estudiante, Matricula, Nota, Seccion

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import ComprobantePdfMixin, ExportarMixin, UsuarioRegistroMixin
from .forms import FiltroUniversidadForm, UniversidadForm
from .models import Universidad













# Vista de inicio del sistema académico
def inicio(request):
    return render(request, "academico/inicio.html")


# Vista para registrar y listar estudiantes
def estudiantes(request):
    if request.method == "POST":
        form = EstudianteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("academico:catalogo")
    else:
        form = EstudianteForm()

    lista_estudiantes = Estudiante.objects.select_related("carrera").all()
    contexto = {
        "form": form,
        "estudiantes": lista_estudiantes,
    }
    return render(request, "academico/estudiantes.html", contexto)


# Vista de catálogo filtrable por carrera y jornada
def catalogo(request):
    form = CatalogoForm(request.GET or None)
    carreras = Carrera.objects.select_related("facultad").prefetch_related("cursos__semestre")
    secciones = Seccion.objects.select_related("curso__carrera", "curso__semestre", "periodo", "profesor")

    carrera_seleccionada = None
    jornada_seleccionada = ""

    if form.is_valid():
        carrera_seleccionada = form.cleaned_data.get("carrera")
        jornada_seleccionada = form.cleaned_data.get("jornada")

        if carrera_seleccionada:
            carreras = carreras.filter(pk=carrera_seleccionada.pk)
            secciones = secciones.filter(curso__carrera=carrera_seleccionada)

        if jornada_seleccionada:
            secciones = secciones.filter(jornada=jornada_seleccionada)

    contexto = {
        "form": form,
        "carreras": carreras,
        "secciones": secciones,
        "carrera_seleccionada": carrera_seleccionada,
        "jornada_seleccionada": jornada_seleccionada,
    }
    return render(request, "academico/catalogo.html", contexto)


# Vista basada en clases para crear matrículas y mostrar el listado
class MatriculaCreateView(CreateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = "academico/matriculas.html"
    success_url = reverse_lazy("academico:matriculas")

    def form_valid(self, form):
        # Guarda la matrícula y asegura que exista su registro de Nota (relación 1:1)
        response = super().form_valid(form)
        Nota.objects.get_or_create(matricula=self.object)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matriculas"] = (
            Matricula.objects.select_related(
                "estudiante__carrera",
                "seccion__curso",
                "seccion__periodo",
                "nota",
            )
            .all()
        )
        return context


# Vista basada en clases para eliminar una matrícula
class MatriculaDeleteView(DeleteView):
    model = Matricula
    template_name = "academico/matricula_confirm_delete.html"
    success_url = reverse_lazy("academico:matriculas")


# Vista basada en clases para registrar o editar las notas (n1, n2, n3) de una matrícula
class MatriculaNotaUpdateView(View):
    template_name = "academico/Nota.html"
    success_url = reverse_lazy("academico:matriculas")

    def _get_matricula_y_nota(self, pk):
        # Busca la matrícula por su id y crea/recupera su nota asociada
        matricula = get_object_or_404(Matricula, pk=pk)
        nota, _ = Nota.objects.get_or_create(matricula=matricula)
        return matricula, nota

    def get(self, request, pk):
        matricula, nota = self._get_matricula_y_nota(pk)
        form = NotaForm(instance=nota)
        return render(
            request,
            self.template_name,
            {"form": form, "matricula": matricula, "nota": nota},
        )

    def post(self, request, pk):
        matricula, nota = self._get_matricula_y_nota(pk)
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            # Al guardar Nota, el modelo calcula automáticamente el promedio y el estado (>= 70)
            form.save()
            return redirect(self.success_url)
        return render(
            request,
            self.template_name,
            {"form": form, "matricula": matricula, "nota": nota},
        )



class UniversidadCreateView(LoginRequiredMixin, UsuarioRegistroMixin, SuccessMessageMixin, CreateView):
    model = Universidad
    form_class = UniversidadForm
    template_name = "academico/universidad_form.html"
    success_url = reverse_lazy("academico:universidad_lista")
    success_message = "Universidad creada correctamente."
    

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