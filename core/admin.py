from django.contrib import admin

from academico.models import (
    Carrera,
    Curso,
    Estudiante,
    Facultad,
    Matricula,
    Nota,
    Periodo,
    Profesor,
    Seccion,
    Semestre,
    Universidad,
)


@admin.register(Universidad)
class UniversidadAdmin(admin.ModelAdmin):
    list_display = ("siglas", "nombre", "ciudad", "fecha_creacion")
    search_fields = ("siglas", "nombre", "ciudad")


@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "universidad", "decano")
    list_filter = ("universidad",)
    search_fields = ("nombre", "decano")


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "facultad", "duracion_semestres")
    list_filter = ("facultad",)
    search_fields = ("codigo", "nombre")


@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    list_display = ("numero", "nombre")
    ordering = ("numero",)


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha_inicio", "fecha_fin", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "carrera", "semestre", "creditos")
    list_filter = ("carrera", "semestre")
    search_fields = ("codigo", "nombre")


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ("cedula", "apellidos", "nombres", "titulo", "email")
    search_fields = ("cedula", "apellidos", "nombres", "email")


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ("cedula", "apellidos", "nombres", "carrera", "email")
    list_filter = ("carrera",)
    search_fields = ("cedula", "apellidos", "nombres", "email")


@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ("curso", "periodo", "paralelo", "jornada", "profesor", "cupo", "inscritos")
    list_filter = ("periodo", "jornada", "curso__carrera")
    search_fields = ("curso__codigo", "curso__nombre", "profesor__apellidos", "profesor__nombres")


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "seccion", "fecha")
    list_filter = ("seccion__periodo", "seccion__jornada")
    search_fields = ("estudiante__cedula", "estudiante__apellidos", "estudiante__nombres", "seccion__curso__codigo")


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ("matricula", "n1", "n2", "n3", "promedio", "estado")
    list_filter = ("estado", "matricula__seccion__periodo")
    search_fields = ("matricula__estudiante__cedula", "matricula__estudiante__apellidos", "matricula__estudiante__nombres")