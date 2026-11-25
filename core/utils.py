from io import BytesIO

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from xhtml2pdf import pisa


def valor_campo(objeto, ruta):
    """Lee un atributo, propiedad o método siguiendo una ruta con '__'."""
    for parte in ruta.split("__"):
        if objeto is None:
            return ""
        display = getattr(objeto, f"get_{parte}_display", None)
        if callable(display):
            objeto = display()
        else:
            objeto = getattr(objeto, parte, "")
        if callable(objeto):
            objeto = objeto()
    return "" if objeto is None else objeto


def exportar_excel(titulo, encabezados, filas, nombre_archivo):
    libro = Workbook()
    hoja = libro.active
    hoja.title = (titulo or "Reporte")[:31]
    hoja.append([titulo])
    hoja["A1"].font = Font(bold=True, size=14)
    hoja.append([])
    hoja.append(encabezados)

    for celda in hoja[3]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="0C4B33")

    for fila in filas:
        hoja.append([v if isinstance(v, (int, float)) else str(v) for v in fila])

    for columna in hoja.columns:
        largo = max(len(str(c.value or "")) for c in columna)
        hoja.column_dimensions[columna[0].column_letter].width = min(largo + 2, 50)

    hoja.freeze_panes = "A4"
    respuesta = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre_archivo}.xlsx"'
    libro.save(respuesta)
    return respuesta


def enlazar_archivos(uri, rel):
    if settings.MEDIA_URL and uri.startswith(settings.MEDIA_URL):
        return str(settings.MEDIA_ROOT / uri.replace(settings.MEDIA_URL, "", 1).lstrip("/\\"))
    if settings.STATIC_URL and uri.startswith(settings.STATIC_URL):
        return str(settings.BASE_DIR / "static" / uri.replace(settings.STATIC_URL, "", 1).lstrip("/\\"))
    return uri


def render_pdf(template, contexto, nombre_archivo, descargar=False):
    html = render_to_string(template, contexto)
    buffer = BytesIO()
    resultado = pisa.CreatePDF(html, dest=buffer, link_callback=enlazar_archivos)
    if resultado.err:
        return HttpResponse("Error al generar el PDF", status=500)
    respuesta = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    modo = "attachment" if descargar else "inline"
    respuesta["Content-Disposition"] = f'{modo}; filename="{nombre_archivo}.pdf"'
    return respuesta