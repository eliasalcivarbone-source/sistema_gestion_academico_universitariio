from django import forms

from .models import Estudiante


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = "__all__"
        exclude = ["creado", "actualizado"]

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
            self.fields["fecha_nacimiento"].widget = forms.DateInput(
                attrs={
                    "type": "date",
                    "class": f"{self.fields['fecha_nacimiento'].widget.attrs.get('class', '')} form-control".strip(),
                }
            )
            
    
from django import forms

from .models import Carrera, Estudiante, Jornada


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = "__all__"
        exclude = ["creado", "actualizado"]

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
            self.fields["fecha_nacimiento"].widget = forms.DateInput(
                attrs={
                    "type": "date",
                    "class": f"{self.fields['fecha_nacimiento'].widget.attrs.get('class', '')} form-control".strip(),
                }
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