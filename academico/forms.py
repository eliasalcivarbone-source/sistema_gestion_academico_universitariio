from django import forms
from .models import Carrera, Estudiante, Jornada, Matricula, Nota, Universidad


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = [
            "cedula",
            "nombres",
            "apellidos",
            "email",
            "telefono",
            "fecha_nacimiento",
            "carrera",
            "foto",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            css_class = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{css_class} form-check-input".strip()
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = f"{css_class} form-select".strip()
            else:
                widget.attrs["class"] = f"{css_class} form-control".strip()

        if "fecha_nacimiento" in self.fields:
            actual_class = self.fields["fecha_nacimiento"].widget.attrs.get("class", "form-control")
            self.fields["fecha_nacimiento"].widget = forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": actual_class,
                },
            )


class CatalogoForm(forms.Form):
    carrera = forms.ModelChoiceField(
        queryset=Carrera.objects.select_related("facultad").all(),
        required=False,
        empty_label="Todas las carreras",
        label="Carrera disponible",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    jornada = forms.ChoiceField(
        choices=[("", "Todas las jornadas")] + list(Jornada.choices),
        required=False,
        label="Jornada",
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ["estudiante", "seccion"]
        labels = {
            "estudiante": "Estudiante",
            "seccion": "Sección / Materia ofertada",
        }
        widgets = {
            "estudiante": forms.Select(attrs={"class": "form-select"}),
            "seccion": forms.Select(attrs={"class": "form-select"}),
        }


class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ["n1", "n2", "n3"]
        labels = {
            "n1": "Nota 1",
            "n2": "Nota 2",
            "n3": "Nota 3",
        }
        widgets = {
            "n1": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "100"}
            ),
            "n2": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "100"}
            ),
            "n3": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0", "max": "100"}
            ),
        }


class UniversidadForm(forms.ModelForm):
    class Meta:
        model = Universidad
        fields = ["nombre", "siglas", "ciudad", "logo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "siglas": forms.TextInput(attrs={"class": "form-control"}),
            "ciudad": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class FiltroUniversidadForm(forms.Form):
    texto = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre o siglas"}),
    )
    ciudad = forms.CharField(
        required=False,
        label="Ciudad",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ciudad"}),
    )