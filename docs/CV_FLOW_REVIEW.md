# Revisión del flujo de CV

- Base: `origin/main`, commit `977ca01` (9 de agosto de 2026).
- Rama de trabajo: `feat/cv-profile-flow`.
- Revisión: 7 de septiembre de 2026.
- El árbol de trabajo estaba limpio al comenzar. No se modificó `main` ni se desplegó el producto.

## Hallazgos verificados y cambios

La interfaz tenía CV estáticos y un botón sin acción. No existían API ni almacenamiento. El agente usaba un pipeline incompleto con importaciones incorrectas. `ProfessionalProfile` solo declaraba datos personales y experiencia, aunque otros componentes añadían secciones dinámicamente. Había incompatibilidades entre el esquema de IA y los constructores de las entidades.

Esta rama implementa:

- Carga multipart de PDF con texto/TXT, validación de tamaño, lectura y mensajes de error.
- `CVAnalyzer` como ruta común del agente, pipeline y API.
- Extracción básica conservadora y análisis opcional con el proveedor existente de LM Studio; selección explícita, sin cambiar silenciosamente de modo.
- Perfil serializable con secciones completas y esquema compartido entre IA y API.
- Edición Flutter de campos y listas, consulta del texto original, confirmación de descarte y conservación de cambios si falla el guardado.
- Persistencia SQLite y endpoints para crear, listar, recuperar y actualizar.
- Selector nativo y cliente HTTP, configurables para backend local.
- Configuración del identificador de modelo con `LMSTUDIO_MODEL`, manteniendo su valor predeterminado.

## Verificación ejecutada

| Comprobación | Resultado |
|---|---|
| `python -m pytest backend/tests/test_cv_flow.py -q` | 18 pruebas aprobadas |
| PDF generado con texto → perfil | Aprobado, extracción real con PyMuPDF |
| TXT → editar todas las listas → guardar → nueva instancia API/SQLite → recuperar → actualizar | Aprobado |
| Archivos vacíos, espacios, binarios TXT, corruptos, formatos no admitidos, exceso de tamaño/texto, PDF sin texto | Rechazados con errores explícitos |
| API y agente comparten resultado | Aprobado |
| Contrato LM Studio con transporte simulado y respuesta inválida | Aprobado; no es una prueba de inferencia real |
| Puerto local 1234 de LM Studio | No había servidor disponible |
| Formateador/parser Dart sobre los cinco archivos del flujo | Ejecutado sin errores de sintaxis |
| Pruebas y análisis Flutter | Pendientes; no ejecutados |
| Compilación Windows y selector nativo real | Pendientes; requieren el equipo Windows |

Las pruebas de Python emitieron dos avisos de deprecación de Starlette/httpx/AnyIO, sin fallos.

La preparación del SDK Flutter 3.41.8 quedó bloqueada por la revisión automática de seguridad: el proceso intentó acceder inesperadamente al endpoint de metadatos del entorno, que podría exponer metadatos o credenciales de la instancia. No se repitió ni se eludió ese acceso. Se utilizó únicamente el formateador Dart ya descargado para una comprobación local sin resolución de paquetes. Esa comprobación no verifica tipos, dependencias ni renderizado. El formateador advirtió que no podía resolver `flutter_lints`.

Se añadieron 4 pruebas de cliente HTTP y 3 de widgets, con API y selector simulados. No se ejecutaron. Las pruebas de widgets utilizan fuentes del sistema para no depender de descargas de Google Fonts. El `pubspec.lock` de Flutter sigue pendiente de regenerarse con `flutter pub get`; no se inventaron hashes de paquetes.

## Archivos principales

- `backend/main.py`: API y recepción de archivos.
- `backend/database/db.py`: SQLite.
- `backend/modules/cv/services/cv_analyzer.py`: análisis común.
- `backend/modules/cv/domain/professional_profile.py`: perfil completo.
- `backend/modules/cv/parser/{profile_mapper,validator,prompt_builder,local_parser}.py`: esquema, validación y extracción.
- `backend/agents/cv_agent/agent.py`: agente conectado al servicio común.
- `apps/employx_flutter/lib/features/cvs/data/cv_api.dart`: cliente HTTP.
- `apps/employx_flutter/lib/features/cvs/views/{my_cvs_screen,profile_editor}.dart`: importación, lista y edición.
- `backend/tests/test_cv_flow.py` y `apps/employx_flutter/test/features/cvs/`: comprobaciones.
- `requirements*.txt` y `docs/CV_FLOW.md`: dependencias e instrucciones.

## Pendientes y siguiente hito

El flujo está implementado, con backend probado. No se declara validado de extremo a extremo con Flutter real.

El siguiente hito es ejecutar `flutter pub get`, `flutter analyze`, las pruebas de CV y el recorrido manual en Windows, primero sin IA y después con el modelo local cargado. Verificar la calidad de extracción con CV representativos, incluyendo secciones y fechas, antes de ampliar a DOCX/OCR o matching de vacantes.

La persistencia es local y de un solo usuario; no incluye autenticación ni concurrencia de edición entre usuarios. No se implementaron generación/exportación de CV ni funciones ajenas a este recorrido.
