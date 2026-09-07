import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class CvApiException implements Exception {
  final String message;
  const CvApiException(this.message);
  @override
  String toString() => message;
}

class CvApi {
  static const maxFileBytes = 10 * 1024 * 1024;
  final http.Client _client;
  final String baseUrl;
  final Duration timeout;

  CvApi({
    http.Client? client,
    String? baseUrl,
    this.timeout = const Duration(minutes: 11),
  }) : _client = client ?? http.Client(),
       baseUrl =
           baseUrl ??
           const String.fromEnvironment(
             'EMPLOYX_API_URL',
             defaultValue: 'http://127.0.0.1:8000',
           );

  Uri _uri(String path) =>
      Uri.parse('${baseUrl.replaceFirst(RegExp(r'/$'), '')}$path');

  Future<dynamic> _request(
    Future<http.Response> Function() send, {
    Duration? deadline,
  }) async {
    try {
      final response = await send().timeout(
        deadline ?? const Duration(seconds: 20),
      );
      dynamic body;
      try {
        body = jsonDecode(utf8.decode(response.bodyBytes));
      } on FormatException {
        throw const CvApiException(
          'El servidor devolvió una respuesta no válida.',
        );
      }
      if (response.statusCode < 200 || response.statusCode >= 300) {
        final detail = body is Map ? body['detail'] : null;
        throw CvApiException(
          detail is String
              ? detail
              : 'No se pudo completar la operación. Revisa los campos e inténtalo de nuevo.',
        );
      }
      return body;
    } on TimeoutException {
      throw const CvApiException(
        'El servidor tardó demasiado. Conserva tus cambios y vuelve a intentar.',
      );
    } on http.ClientException {
      throw const CvApiException(
        'No se pudo conectar con el servidor. Comprueba que el backend esté iniciado y pulsa Reintentar.',
      );
    }
  }

  Future<List<Map<String, dynamic>>> list() async {
    final result = await _request(() => _client.get(_uri('/api/cvs')));
    return (result as List)
        .map((e) => Map<String, dynamic>.from(e as Map))
        .toList();
  }

  Future<Map<String, dynamic>> get(String id) async =>
      Map<String, dynamic>.from(
        await _request(
              () => _client.get(_uri('/api/cvs/${Uri.encodeComponent(id)}')),
            )
            as Map,
      );

  Future<Map<String, dynamic>> analyze(
    String name,
    Uint8List bytes, {
    String mode = 'local',
  }) async {
    final extension = name.split('.').last.toLowerCase();
    if (!['pdf', 'txt'].contains(extension)) {
      throw const CvApiException(
        'Selecciona un PDF con texto o un archivo TXT.',
      );
    }
    if (bytes.isEmpty || bytes.length > maxFileBytes) {
      throw const CvApiException(
        'El archivo está vacío o supera el límite de 10 MB.',
      );
    }
    final request = http.MultipartRequest(
      'POST',
      _uri('/api/cvs/analyze').replace(queryParameters: {'mode': mode}),
    );
    request.files.add(
      http.MultipartFile.fromBytes('file', bytes, filename: name),
    );
    return Map<String, dynamic>.from(
      await _request(
            () async => http.Response.fromStream(await _client.send(request)),
            deadline: timeout,
          )
          as Map,
    );
  }

  Future<Map<String, dynamic>> save(Map<String, dynamic> draft) async {
    final id = draft['id'] as String?;
    final payload = {
      for (final key in [
        'title',
        'profile',
        'source_text',
        'extraction_method',
        'warnings',
      ])
        key: draft[key],
    };
    final uri = _uri(
      id == null ? '/api/cvs' : '/api/cvs/${Uri.encodeComponent(id)}',
    );
    final headers = {'Content-Type': 'application/json'};
    return Map<String, dynamic>.from(
      await _request(
            () => id == null
                ? _client.post(uri, headers: headers, body: jsonEncode(payload))
                : _client.put(uri, headers: headers, body: jsonEncode(payload)),
          )
          as Map,
    );
  }

  void close() => _client.close();
}
