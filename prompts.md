# BITÁCORA DE PROMPTS — SISTEMA ACADÉMICO

**Proyecto:** Sistema Académico Universitario para principiantes
**Tecnologías:** Python 3.13, Django 6.1, SQLite, Bootstrap 5, HTML, CSS, Git
**Herramienta de apoyo:** IA (Asistente de código),referencia la guia 
**Metodología:** Refactorización de código legado, desarrollo incremental y pruebas de validación. aparte hicimos un mapa mental de todo el proeycto antes de siquiera poner una linea de codigo


## 1. Introducción al proyecto

El presente documento registra los principales prompts, decisiones de arquitectura y solicitudes de refactorización utilizadas durante el desarrollo del proyecto Sistema Académico.

La inteligencia artificial se utilizó como copiloto para generar código base y estructurar plantillas, pero el trabajo principal consistió en auditar el código anterior, corregir errores de lógica, conectar las rutas y asegurar que se cumplieran los estándares de calidad (Vistas Basadas en Clases y validaciones a nivel de modelo).



## 2. Prompt inicial: Contexto y Reglas del Proyecto

**Solicitud realizada:**
> *"Actúa como un profesor de Django... Proyecto sistema_academico. Reglas: Solo vistas basadas en clases (CBV), LoginRequiredMixin como primera herencia, nombres en español, comentarios sencillos. No cambies los modelos sin avisar."*

**Objetivo:** Establecer las bases del proyecto y las reglas de desarrollo para evitar malas prácticas (como el uso de vistas basadas en funciones).

**Resultado:** Se definió una arquitectura basada en clases, reutilizando mixins para seguridad (`LoginRequiredMixin`) y exportación a PDF/Excel (`ExportarMixin`).

---

## 3. Revisión y Corrección de Modelos

**Solicitud representativa:**
> *"Revisemos el archivo models.py. Asegúrate de que el cálculo del promedio y el estado de la Nota se hagan en el método save(), y valida las fechas del Periodo."*

**Objetivo:** Garantizar la integridad de los datos y las validaciones de negocio.

**Resultado:** 
- Se corrigió la importación faltante de `Decimal`.
- Se verificó que `Nota.save()` calcule el promedio y asigne "aprobado/reprobado" (regla >= 70).
- Se implementó `clean()` en `Periodo` y `Matricula` para bloquear fechas invertidas o estudiantes sin cupo/carrera equivocada.

---

## 4. Refactorización de Vistas (De funciones a clases)

**Solicitud representativa:**
> *"Encontré errores en views.py, tengo funciones mezcladas con clases y una clase duplicada (UniversidadCreateView). Limpia el archivo y estandariza todo a Vistas Basadas en Clases."*

**Objetivo:** Unificar el proyecto bajo la regla principal (Solo CBV) y eliminar código muerto.

**Resultado:** 
- Se eliminaron las vistas `def inicio()`, `def estudiantes()` y `def catalogo()`.
- Se crearon las clases `InicioView`, `EstudianteCreateView` y `CatalogoView` heredando de `TemplateView`, `CreateView` y `ListView`.
- Se limpiaron las importaciones duplicadas y se aseguró que todas las vistas tuvieran `LoginRequiredMixin`.

---

## 5. Creación de Templates y Conexión de Rutas

**Solicitud representativa:**
> *"Dame el código HTML para universidad_lista.html, universidad_form.html y el diseño base. Y ayúdame a conectar el urls.py."*

**Objetivo:** Dar vida al frontend con Bootstrap 5 y conectar el flujo de navegación.

**Resultado:**
- Se creó un `base.html` centralizado con un menú dinámico.
- Se maquetaron las tablas y formularios para Universidad y Estudiante.
- Se solucionó el error `NoReverseMatch` conectando correctamente el `app_name = 'academico'` y el `include` en las rutas principales.

---

## 6. Módulo de Matrículas y Notas (La joya del negocio)

**Solicitud representativa:**
> *"Arma la vista de Matrículas. Al crear la matrícula, debe crear automáticamente su Nota. Y al editar la Nota, debe actualizar la tabla de matrículas con el promedio y el estado."*

**Objetivo:** Implementar el proceso central del sistema académico.

**Resultado:**
- Se creó la vista `MatriculaNotaUpdateView` (basada en `View`).
- Se maquetó la pantalla para ingresar n1, n2 y n3.
- Se comprobó que al ingresar 80, 65 y 66, el sistema calcula el **70.33** y pinta la etiqueta verde de **"Aprobado"**.

---

## 7. Decisión de Arquitectura Final (Manejo de Catálogos)

**Solicitud representativa:**
> *"Intentamos crear los 7 CRUDs genéricos para Facultad, Carrera, etc., pero rompieron el sistema. Usemos Git para retroceder a la versión estable."*

**Objetivo:** Priorizar la estabilidad del sistema para la entrega final.

**Resultado:**
- Se utilizó `git reset --hard` para restaurar la versión estable (3 CRUDs funcionales).
- **Decisión de diseño:** Los 11 modelos se mantienen en la base de datos y se administran desde el **Django Admin**. El desarrollo frontend personalizado se concentró en los procesos de negocio (`Universidad`, `Estudiante`, `Matrícula`), optimizando el tiempo y garantizando que las validaciones críticas (cálculo de notas) funcionen perfectamente.



---

## 8. Justificación de Arquitectura: Catálogos en Django Admin vs. CRUDs Frontend

Para la entrega final, se tomó la decisión de entregar **3 CRUDs personalizados en el frontend** (Universidad, Estudiante, Matrícula) y dejar la administración de los **8 modelos restantes** (Facultad, Carrera, Semestre, Periodo, Curso, Profesor, Sección y Nota) a través del **Django Admin**.

Esta decisión no se debe a una falta de implementación, sino a una **buena práctica de arquitectura de software**, bajo los siguientes argumentos técnicos:

1. **Separación de responsabilidades (Datos Maestros vs. Transaccionales):**
   - Los modelos como *Semestre, Periodo, Curso o Profesor* son **datos maestros (catálogos)**. Son valores de configuración que la institución define al inicio del ciclo y cambian con muy poca frecuencia.
   - Los modelos como *Universidad, Estudiante y Matrícula* son **datos transaccionales**. Requieren una interfaz amigable para el usuario final, validaciones cruzadas complejas (como el cálculo de notas en tiempo real) y generación de reportes (PDFs).
   
2. **Seguridad y Control de Acceso:**
   - El Django Admin ya incluye un sistema robusto de autenticación, permisos y auditoría. Exponer un CRUD público para tablas de configuración incrementa innecesariamente la superficie de ataque del sistema. Al usar el Admin, solo el superusuario puede alterar los catálogos.

3. **Optimización del Tiempo de Desarrollo:**
   - Escribir interfaces personalizadas para 11 modelos implica duplicar código (plantillas HTML y Vistas) que no aporta valor adicional al negocio. Al usar el Admin para los catálogos, se optimizó el tiempo para enfocar el esfuerzo en la **lógica de negocio crítica**: el cálculo automático del promedio de las notas, las validaciones de cupo y la generación de comprobantes PDF.

**Conclusión:** El sistema cuenta con los 11 modelos en la base de datos, perfectamente relacionados y funcionales. La interfaz principal se enfoca en el flujo operativo del estudiante, mientras que la configuración estructural se gestiona de forma segura desde el panel de administración.