# Primer flujo de CV — LIA-EmployX

## Alcance

Seleccionar PDF con texto o TXT → analizar → revisar/editar → guardar → volver a abrir.

La pantalla **Mis CVs** consulta datos reales del backend. Los demás módulos conservan su estado anterior; esta entrega no implementa búsqueda de empleo ni agentes autónomos.

- **Extracción básica sin IA** (predeterminada): extrae literalmente el correo y los campos con etiquetas `Nombre:`, `Nombre completo:`, `Teléfono:`, `Ciudad:` y `País:` (también algunas variantes en inglés). No identifica automáticamente experiencia o estudios. Los campos ausentes quedan vacíos; el texto original está disponible para completarlos manualmente.
- **Analizar con LM Studio**: usa el proveedor existente para extraer el perfil completo. No cambia automáticamente a modo local si falla. Hay que revisar los datos antes de guardarlos.
- PDF escaneado, imágenes y DOCX quedan pendientes en este flujo. Los lectores anteriores de DOCX/OCR se conservan, pero no se cargan ni requieren sus dependencias para este MVP.
- Límites: 10 MiB por archivo y 60 000 caracteres de texto. No se trunca silenciosamente.
- No se guarda nada al analizar. El botón **Guardar perfil** crea o actualiza el registro.

## Ejecutar en Windows (PowerShell)

Requisitos: Python 3.11 o superior; Flutter compatible con Dart 3.11.5 o superior. Para Windows escritorio, Visual Studio con la carga de desarrollo de escritorio con C++. Chrome es una alternativa para probar el flujo sin compilar Windows.

Desde la raíz de tu copia del repositorio, en la rama `feat/cv-profile-flow`:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

`requirements.txt` declara dependencias de ejecución; `requirements-dev.txt` añade pruebas. `requirements-lock.txt` fija las versiones utilizadas durante esta revisión (incluye herramientas de prueba).

En otra terminal, desde la raíz:

```powershell
cd apps\employx_flutter
flutter pub get
flutter run -d windows --dart-define=EMPLOYX_API_URL=http://127.0.0.1:8000
```

Alternativa web:

```powershell
flutter run -d chrome --web-port 5173 --dart-define=EMPLOYX_API_URL=http://127.0.0.1:8000
```

La URL del backend es un parámetro de compilación: vuelve a ejecutar Flutter cuando la cambies. CORS admite por defecto `http://localhost:5173` y `http://127.0.0.1:5173`. Se puede configurar `EMPLOYX_CORS_ORIGINS` en el proceso Python con una lista separada por comas.

Abre **Mis CVs**, selecciona **Extracción básica sin IA** y pulsa **Nuevo CV**. Puedes crear un TXT de prueba con:

```text
Nombre: Persona de prueba
Correo: demo@example.com
Teléfono: 5551234567
Ciudad: Monterrey

Experiencia laboral
Empresa de prueba — Asesor de ventas
```

El correo y los campos etiquetados se extraen. La experiencia se completa con **Añadir: Experiencia**, consultando el texto original. Cambia el nombre del perfil, guarda, cierra la app y reinicia el backend. Al abrir **Mis CVs**, el registro debe seguir disponible.

Si una operación falla, el mensaje explica el problema. Un fallo al guardar mantiene el formulario abierto con los cambios. Cancelar un formulario modificado pide confirmar su descarte.

## LM Studio (opcional)

Inicia el servidor local de LM Studio y carga tu modelo. Antes de iniciar Python puedes configurar:

```powershell
$env:LMSTUDIO_HOST = "127.0.0.1"
$env:LMSTUDIO_PORT = "1234"
$env:LMSTUDIO_MODEL = "identificador-exacto-del-modelo-cargado"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Se conserva `google/gemma-4-e4b` como identificador predeterminado del repositorio. El identificador configurado debe coincidir con el que devuelve tu servidor en `/v1/models`. No se descarga ningún modelo ni se introduce un proveedor externo. El análisis puede tardar varios minutos en una GPU pequeña.

## Persistencia y API

SQLite almacena el perfil, título, texto original, método de extracción, avisos y fechas en `backend/data/employx.sqlite`, excluido de Git. El archivo fuente se procesa en un directorio temporal y se elimina después del análisis. Cambiar o borrar la base cambia o elimina los perfiles disponibles.

Puedes elegir otra ubicación estable antes de iniciar el backend:

```powershell
$env:EMPLOYX_DB_PATH = "D:\DatosEmployX\employx.sqlite"
```

Este servicio es para desarrollo local de un solo usuario y se inicia en loopback. No incluye autenticación ni separación de perfiles por usuario; no está preparado para publicarlo o exponerlo en una red compartida.

| Método | Ruta | Resultado |
|---|---|---|
| GET | `/health` | Servicio y SQLite disponibles |
| POST | `/api/cvs/analyze?mode=local` | Multipart `file`; borrador sin guardar |
| POST | `/api/cvs/analyze?mode=lmstudio` | Borrador analizado con proveedor existente |
| GET | `/api/cvs` | Lista resumida de perfiles |
| POST | `/api/cvs` | Guarda un borrador revisado |
| GET | `/api/cvs/{id}` | Recupera el perfil completo |
| PUT | `/api/cvs/{id}` | Actualiza el mismo registro |

Contrato interactivo: `http://127.0.0.1:8000/docs`. Errores: 413 archivo grande; 415 formato no admitido; 422 archivo o datos no válidos; 503 análisis de LM Studio fallido; 404 perfil ausente.

`CVAnalyzer` es la ruta común de la API y `CVAgent`; `SmartCVPipeline` delega en ella. `ProfessionalProfile` y sus dataclasses definen el perfil; Pydantic valida y serializa la estructura, incluso las listas anidadas. El prompt de IA utiliza ese mismo esquema.

## Verificación

Desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_cv_flow.py -q
cd apps\employx_flutter
flutter analyze
flutter test test/features/cvs
```

Los scripts históricos `test_nvidia*`, `test_ai.py` y otros requieren servicios, entradas interactivas o archivos personales. No forman parte de esta suite automatizada; no se ejecutan al usar el comando específico anterior.

Las pruebas de contrato con LM Studio sustituyen el transporte o el parser por dobles controlados. No son evidencia de calidad de extracción de un modelo real. Las pruebas de Flutter sustituyen el selector nativo y la API; la integración manual con un selector real queda indicada en el informe de revisión.

## Referencias de implementación

- [FastAPI: carga de archivos](https://fastapi.tiangolo.com/tutorial/request-files/)
- [file_picker: selector multiplataforma](https://pub.dev/packages/file_picker)
- [http: cliente HTTP de Dart](https://pub.dev/packages/http)
