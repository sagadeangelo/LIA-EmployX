class EnvConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000/api/v1',
  );
  
  static const int connectTimeout = 15000;
  static const int receiveTimeout = 15000;
}
