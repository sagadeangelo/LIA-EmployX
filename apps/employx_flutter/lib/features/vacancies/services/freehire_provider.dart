import 'package:dio/dio.dart';

import '../../../core/config/env_config.dart';
import '../models/vacancy_model.dart';

/// Cliente de acceso a FreeHire.
///
/// FreeHire funciona como fuente externa de vacantes.
/// Esta clase se encarga exclusivamente de:
///
/// 1. Consultar la API.
/// 2. Interpretar su respuesta.
/// 3. Convertir cada registro a VacancyModel.
///
/// La aplicación no debe depender directamente del formato
/// interno de FreeHire después de esta capa.
class FreeHireProvider {
  /// Base URL del proxy en el backend de LIA.
  ///
  /// Flutter Web no puede llamar directamente a https://freehire.me porque
  /// FreeHire no devuelve Access-Control-Allow-Origin en sus respuestas CORS.
  /// El backend de LIA actúa como proxy transparente: recibe la petición
  /// desde Flutter y la reenvía a FreeHire server-side, evitando el bloqueo
  /// del browser.
  static String get _baseUrl => EnvConfig.baseUrl;

  final Dio _dio;

  FreeHireProvider({
    Dio? dio,
  }) : _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: _baseUrl,
                connectTimeout: const Duration(seconds: 15),
                receiveTimeout: const Duration(seconds: 20),
                headers: const {
                  'Accept': 'application/json',
                },
              ),
            );

  /// Busca vacantes en FreeHire.
  ///
  /// [query] debe contener únicamente contexto profesional:
  /// cargo, skills relevantes. NO debe contener ubicación.
  ///
  /// [countries] acepta uno o varios códigos ISO 3166-1 alpha-2
  /// separados por coma (ej. "mx", "mx,us"). Este es el único
  /// mecanismo de filtrado geográfico real que soporta FreeHire
  /// en /jobs/search. Parámetros como location, city, region o
  /// country son ignorados por la API.
  ///
  /// [limit] y [offset] controlan la paginación.
  Future<List<VacancyModel>> searchJobs({
    String query = '',
    String countries = '',
    int limit = 20,
    int offset = 0,
  }) async {
    final trimmedQuery = query.trim();
    final trimmedCountries = countries.trim();

    final response = await _dio.get(
      '/jobs/search',
      queryParameters: {
        if (trimmedQuery.isNotEmpty) 'q': trimmedQuery,
        if (trimmedCountries.isNotEmpty) 'countries': trimmedCountries,
        'limit': limit,
        'offset': offset,
      },
    );

    return _parseJobsResponse(response.data);
  }

  /// Obtiene vacantes sin aplicar una búsqueda específica.
  ///
  /// Se utilizará posteriormente para la carga inicial de Job Hunter.
  Future<List<VacancyModel>> getJobs({
    int limit = 20,
    int offset = 0,
  }) async {
    final response = await _dio.get(
      '/jobs',
      queryParameters: {
        'limit': limit,
        'offset': offset,
      },
    );

    return _parseJobsResponse(response.data);
  }

  List<VacancyModel> _parseJobsResponse(dynamic data) {
    if (data is! Map<String, dynamic>) {
      throw const FormatException(
        'Respuesta inválida de FreeHire: se esperaba un objeto JSON.',
      );
    }

    final dynamic rawJobs = data['data'];

    if (rawJobs is! List) {
      return const [];
    }

    return rawJobs
        .whereType<Map>()
        .map(
          (job) => VacancyModel.fromJson(
            _normalizeJob(job.cast<String, dynamic>()),
          ),
        )
        .toList();
  }

  /// Convierte el esquema de FreeHire al contrato interno
  /// de LIA-EmployX.
  Map<String, dynamic> _normalizeJob(
    Map<String, dynamic> job,
  ) {
    final enrichment = _asMap(job['enrichment']);

    final salaryMin = _firstValue(
      job['salary_min'],
      enrichment['salary_min'],
    );

    final salaryMax = _firstValue(
      job['salary_max'],
      enrichment['salary_max'],
    );

    final currency = _firstString(
      job['salary_currency'],
      enrichment['salary_currency'],
      job['currency'],
      enrichment['currency'],
    );

    final experienceLevel = _firstString(
      job['seniority'],
      enrichment['seniority'],
      job['experience_level'],
      enrichment['experience_level'],
    );

    final employmentType = _firstString(
      job['employment_type'],
      enrichment['employment_type'],
    );

    final sourceUrl = _firstString(
      job['url'],
      job['source_url'],
    );

    final applicationUrl = _firstString(
      job['application_url'],
      job['url'],
    );

    final location = _buildLocation(job);

    return {
      'id': _firstString(
        job['public_slug'],
        job['id'],
        job['external_id'],
      ),
      'title': _firstString(job['title']),
      'company': _firstString(job['company']),
      'location': location,
      'modality': _normalizeModality(
        job,
        enrichment,
      ),
      'employment_type': employmentType,
      'experience_level': experienceLevel,
      'salary_min': salaryMin,
      'salary_max': salaryMax,
      'currency': currency,
      'description': _firstString(job['description']),
      'skills': _stringList(job['skills']),
      'source': _firstString(job['source'], 'freehire'),
      'source_url': sourceUrl,
      'application_url': applicationUrl.isEmpty
          ? null
          : applicationUrl,
      'posted_at': job['posted_at'],
    };
  }

  String _buildLocation(
    Map<String, dynamic> job,
  ) {
    final directLocation = _firstString(
      job['location'],
    );

    if (directLocation.isNotEmpty) {
      return directLocation;
    }

    final cities = _stringList(job['cities']);

    if (cities.isNotEmpty) {
      return cities.join(', ');
    }

    final countries = _stringList(job['countries']);

    if (countries.isNotEmpty) {
      return countries.join(', ');
    }

    return _firstString(
      job['regions'],
    );
  }

  String _normalizeModality(
    Map<String, dynamic> job,
    Map<String, dynamic> enrichment,
  ) {
    final direct = _firstString(
      job['modality'],
      job['work_format'],
      enrichment['modality'],
      enrichment['work_format'],
    ).toLowerCase();

    if (direct.contains('remote')) {
      return 'Remote';
    }

    if (direct.contains('hybrid')) {
      return 'Hybrid';
    }

    if (direct.contains('onsite') ||
        direct.contains('on-site') ||
        direct.contains('on site')) {
      return 'On-site';
    }

    final relocation = _firstString(
      job['relocation'],
      enrichment['relocation'],
    ).toLowerCase();

    if (relocation.isNotEmpty) {
      return relocation;
    }

    return '';
  }

  Map<String, dynamic> _asMap(dynamic value) {
    if (value is Map) {
      return value.cast<String, dynamic>();
    }

    return const {};
  }

  dynamic _firstValue(
    dynamic first,
    dynamic second,
  ) {
    if (first != null) {
      return first;
    }

    return second;
  }

  String _firstString([
    dynamic first,
    dynamic second,
    dynamic third,
    dynamic fourth,
  ]) {
    for (final value in [
      first,
      second,
      third,
      fourth,
    ]) {
      if (value == null) {
        continue;
      }

      final text = value.toString().trim();

      if (text.isNotEmpty) {
        return text;
      }
    }

    return '';
  }

  List<String> _stringList(dynamic value) {
    if (value is! List) {
      return const [];
    }

    return value
        .map(
          (item) => item.toString().trim(),
        )
        .where(
          (item) => item.isNotEmpty,
        )
        .toList();
  }
}