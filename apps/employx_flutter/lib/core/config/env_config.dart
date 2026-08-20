class EnvConfig {
  // La URL base del backend se puede sobreescribir en tiempo de compilación/ejecución.
  //
  // Para desarrollo local (default):
  // flutter run -d web-server
  //
  // Para Producción (despliegue en LIA-Tech):
  // flutter build web --dart-define=API_BASE_URL=https://api.lia-tech.com
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8001/api/v1',
  );

  static const int connectTimeout = 15000;

  // El procesamiento de CV puede incluir OCR,
  // extracción DOCX y construcción del ProfessionalProfile.
  //
  // Algunos CV tardan más de 60 segundos.
  // Permitimos hasta 3 minutos.
  static const int receiveTimeout = 180000;
}