from django.shortcuts import redirect, render

from .forms import CatalogoForm, EstudianteForm
from .models import Carrera, Estudiante, Seccion


def inicio(request):
    return render(request, "academico/inicio.html")


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