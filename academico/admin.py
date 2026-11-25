from django.contrib import admin
from .models import Matricula, Nota

admin.site.unregister(Nota)


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ("id", "matricula", "n1", "n2", "n3", "promedio", "estado")
    list_filter = ("estado",)
    readonly_fields = ("promedio", "estado")


admin.site.unregister(Matricula)
admin.site.register(Matricula)


