from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from academico.models import (
    Carrera,
    Curso,
    Estudiante,
    Facultad,
    Jornada,
    Matricula,
    Nota,
    Periodo,
    Profesor,
    Seccion,
    Semestre,
    Universidad,
)


class Command(BaseCommand):
    help = "Puebla la base de datos con datos de prueba del sistema académico"

    @transaction.atomic
    def handle(self, *args, **options):
        universidad, _ = Universidad.objects.get_or_create(
            nombre="Universidad Estatal de Milagro",
            defaults={
                "siglas": "UNEMI",
                "ciudad": "Milagro",
            },
        )

        facultad, _ = Facultad.objects.get_or_create(
            universidad=universidad,
            nombre="Facultad de Ciencias e Ingeniería",
            defaults={"decano": "Dr. Carlos Mendoza"},
        )

        carrera, _ = Carrera.objects.get_or_create(
            codigo="SIS",
            defaults={
                "facultad": facultad,
                "nombre": "Ingeniería en Software",
                "duracion_semestres": 8,
            },
        )

        semestre_1, _ = Semestre.objects.get_or_create(
            numero=1,
            defaults={"nombre": "Primer semestre"},
        )
        semestre_2, _ = Semestre.objects.get_or_create(
            numero=2,
            defaults={"nombre": "Segundo semestre"},
        )

        periodo, _ = Periodo.objects.get_or_create(
            nombre="2026-1",
            defaults={
                "fecha_inicio": date(2026, 5, 1),
                "fecha_fin": date(2026, 9, 30),
                "activo": True,
            },
        )

        curso_1, _ = Curso.objects.get_or_create(
            codigo="SIS-101",
            defaults={
                "carrera": carrera,
                "semestre": semestre_1,
                "nombre": "Fundamentos de Programación",
                "creditos": 4,
            },
        )
        curso_2, _ = Curso.objects.get_or_create(
            codigo="SIS-201",
            defaults={
                "carrera": carrera,
                "semestre": semestre_2,
                "nombre": "Estructuras de Datos",
                "creditos": 4,
            },
        )

        profesor_1, _ = Profesor.objects.get_or_create(
            cedula="0912345678",
            defaults={
                "nombres": "Andrés",
                "apellidos": "Zambrano",
                "email": "azambrano@ejemplo.edu.ec",
                "titulo": "Mg. en Ciencias de la Computación",
            },
        )
        profesor_2, _ = Profesor.objects.get_or_create(
            cedula="0987654321",
            defaults={
                "nombres": "Valeria",
                "apellidos": "Quintero",
                "email": "vquintero@ejemplo.edu.ec",
                "titulo": "Ing. en Sistemas",
            },
        )

        estudiante_1, _ = Estudiante.objects.get_or_create(
            cedula="0923456789",
            defaults={
                "nombres": "Mateo",
                "apellidos": "Salazar",
                "email": "msalazar@ejemplo.edu.ec",
                "telefono": "0991112233",
                "fecha_nacimiento": date(2004, 3, 15),
                "carrera": carrera,
            },
        )
        estudiante_2, _ = Estudiante.objects.get_or_create(
            cedula="0934567890",
            defaults={
                "nombres": "Camila",
                "apellidos": "Paredes",
                "email": "cparedes@ejemplo.edu.ec",
                "telefono": "0994445566",
                "fecha_nacimiento": date(2005, 7, 22),
                "carrera": carrera,
            },
        )

        seccion_1, _ = Seccion.objects.get_or_create(
            curso=curso_1,
            periodo=periodo,
            paralelo="A",
            jornada=Jornada.DIURNA,
            defaults={
                "profesor": profesor_1,
                "cupo": 30,
            },
        )
        seccion_2, _ = Seccion.objects.get_or_create(
            curso=curso_2,
            periodo=periodo,
            paralelo="B",
            jornada=Jornada.NOCTURNA,
            defaults={
                "profesor": profesor_2,
                "cupo": 25,
            },
        )

        matricula_1, _ = Matricula.objects.get_or_create(
            estudiante=estudiante_1,
            seccion=seccion_1,
        )
        matricula_2, _ = Matricula.objects.get_or_create(
            estudiante=estudiante_2,
            seccion=seccion_2,
        )

        Nota.objects.get_or_create(
            matricula=matricula_1,
            defaults={
                "n1": Decimal("85.00"),
                "n2": Decimal("90.00"),
                "n3": Decimal("88.00"),
            },
        )
        Nota.objects.get_or_create(
            matricula=matricula_2,
            defaults={
                "n1": Decimal("65.00"),
                "n2": Decimal("70.00"),
                "n3": Decimal("62.00"),
            },
        )

        self.stdout.write(self.style.SUCCESS("Datos de prueba poblados correctamente."))