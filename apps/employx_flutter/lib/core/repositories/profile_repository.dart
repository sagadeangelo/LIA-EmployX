import 'package:dio/dio.dart';

import '../api/api_client.dart';
import '../models/professional_profile_model.dart';
import '../utils/app_logger.dart';
import '../../features/profile/models/cv_document.dart';

class ProfileRepository {
  final ApiClient _apiClient;

  ProfileRepository({
    ApiClient? apiClient,
  }) : _apiClient = apiClient ?? ApiClient();

  // =====================================================================
  // PROFESSIONAL PROFILE
  // =====================================================================

  Future<ProfessionalProfile?> getProfile(
    String profileId,
  ) async {
    final normalizedId = profileId.trim();

    if (normalizedId.isEmpty) {
      AppLogger.warning(
        'ProfileRepository',
        'No se puede cargar un perfil con ID vacío.',
      );

      return null;
    }

    try {
      AppLogger.info(
        'ProfileRepository',
        'Solicitando ProfessionalProfile [$normalizedId]',
      );

      final response = await _apiClient.get(
        '/profile/$normalizedId',
      );

      if (response.statusCode != 200) {
        AppLogger.warning(
          'ProfileRepository',
          'Perfil [$normalizedId] no encontrado. '
          'Status: ${response.statusCode}',
        );

        return null;
      }

      final data = response.data;

      if (data is Map<String, dynamic>) {
        return ProfessionalProfile.fromJson(data);
      }

      if (data is Map) {
        return ProfessionalProfile.fromJson(
          Map<String, dynamic>.from(data),
        );
      }

      AppLogger.error(
        'ProfileRepository',
        'La respuesta del perfil tiene un formato inválido.',
      );

      return null;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        AppLogger.warning(
          'ProfileRepository',
          'Profile $normalizedId no encontrado.',
        );

        return null;
      }

      AppLogger.error(
        'ProfileRepository',
        'Error obteniendo Profile $normalizedId: ${e.message}',
      );

      rethrow;
    } catch (e) {
      AppLogger.error(
        'ProfileRepository',
        'Error inesperado obteniendo Profile $normalizedId: $e',
      );

      rethrow;
    }
  }

  // =====================================================================
  // USER CVS
  // =====================================================================

  Future<List<CVDocument>> getCVs() async {
    try {
      AppLogger.info(
        'ProfileRepository',
        'Solicitando CVs del usuario actual.',
      );

      final response = await _apiClient.get(
        '/cv',
      );

      if (response.statusCode != 200) {
        AppLogger.warning(
          'ProfileRepository',
          'No se pudieron obtener los CVs. '
          'Status: ${response.statusCode}',
        );

        return const <CVDocument>[];
      }

      final data = response.data;

      if (data is List) {
        final cvs = <CVDocument>[];

        for (final item in data) {
          if (item is! Map) {
            AppLogger.warning(
              'ProfileRepository',
              'Elemento de CV ignorado porque no es un objeto JSON.',
            );
            continue;
          }

          try {
            final mapped = _mapBackendCv(
              Map<String, dynamic>.from(item),
            );

            cvs.add(mapped);
          } catch (e) {
            AppLogger.warning(
              'ProfileRepository',
              'No se pudo convertir un CV recibido del backend: $e',
            );
          }
        }

        AppLogger.info(
          'ProfileRepository',
          'CVs recuperados correctamente: ${cvs.length}',
        );

        return List<CVDocument>.unmodifiable(cvs);
      }

      // ---------------------------------------------------------------
      // Compatibilidad defensiva con:
      //
      // {
      //   "cvs": [...]
      // }
      // ---------------------------------------------------------------

      if (data is Map) {
        final map = Map<String, dynamic>.from(data);
        final rawCvs = map['cvs'];

        if (rawCvs is List) {
          final cvs = <CVDocument>[];

          for (final item in rawCvs) {
            if (item is! Map) {
              continue;
            }

            try {
              cvs.add(
                _mapBackendCv(
                  Map<String, dynamic>.from(item),
                ),
              );
            } catch (e) {
              AppLogger.warning(
                'ProfileRepository',
                'No se pudo convertir un CV del contenedor: $e',
              );
            }
          }

          AppLogger.info(
            'ProfileRepository',
            'CVs recuperados desde contenedor: ${cvs.length}',
          );

          return List<CVDocument>.unmodifiable(cvs);
        }
      }

      AppLogger.error(
        'ProfileRepository',
        'La respuesta de /cv tiene un formato inválido.',
      );

      return const <CVDocument>[];
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        AppLogger.warning(
          'ProfileRepository',
          'Endpoint /cv no encontrado.',
        );

        return const <CVDocument>[];
      }

      AppLogger.error(
        'ProfileRepository',
        'Error obteniendo CVs: ${e.message}',
      );

      rethrow;
    } catch (e) {
      AppLogger.error(
        'ProfileRepository',
        'Error inesperado obteniendo CVs: $e',
      );

      rethrow;
    }
  }

  // =====================================================================
  // BACKEND CV -> FLUTTER CV
  // =====================================================================

  CVDocument _mapBackendCv(
    Map<String, dynamic> json,
  ) {
    final metadata = _asMap(
      json['metadata'],
    );

    final contact = _asMap(
      json['contact'],
    );

    final id = _string(
      json['id'],
    );

    if (id.isEmpty) {
      throw const FormatException(
        'El CV recibido no contiene id.',
      );
    }

    final professionalProfileId = _nullable(
      json['professional_profile_id'] ??
          json['professionalProfileId'],
    );

    final originalName = _string(
      metadata['original_name'] ??
          metadata['file_name'],
    );

    final storagePath = _nullable(
      metadata['storage_path'],
    );

    final fullName = _string(
      contact['full_name'],
    );

    final uploadedAt = _date(
      metadata['uploaded_at'],
    );

    final processedAt = _dateOrNull(
      metadata['processed_at'],
    );

    return CVDocument(
      id: id,
      displayName: fullName.isNotEmpty
          ? fullName
          : _displayNameFromFile(
              originalName,
            ),
      fileName: originalName.isNotEmpty
          ? originalName
          : 'CV',
      localPath: null,
      remotePath: storagePath,
      professionalProfileId:
          professionalProfileId,
      createdAt: uploadedAt,
      updatedAt: processedAt ?? uploadedAt,
      isActive: false,
    );
  }

  // =====================================================================
  // JSON HELPERS
  // =====================================================================

  static Map<String, dynamic> _asMap(
    dynamic value,
  ) {
    if (value is Map<String, dynamic>) {
      return value;
    }

    if (value is Map) {
      return Map<String, dynamic>.from(value);
    }

    return const <String, dynamic>{};
  }

  static String _string(
    dynamic value,
  ) {
    return value?.toString().trim() ?? '';
  }

  static String? _nullable(
    dynamic value,
  ) {
    final result = _string(value);

    return result.isEmpty ? null : result;
  }

  static DateTime _date(
    dynamic value,
  ) {
    if (value is DateTime) {
      return value;
    }

    final parsed = DateTime.tryParse(
      value?.toString() ?? '',
    );

    return parsed ??
        DateTime.fromMillisecondsSinceEpoch(0);
  }

  static DateTime? _dateOrNull(
    dynamic value,
  ) {
    if (value == null) {
      return null;
    }

    if (value is DateTime) {
      return value;
    }

    return DateTime.tryParse(
      value.toString(),
    );
  }

  static String _displayNameFromFile(
    String fileName,
  ) {
    if (fileName.isEmpty) {
      return 'CV';
    }

    final lastSlash = fileName.lastIndexOf(
      RegExp(r'[/\\]'),
    );

    final name = lastSlash >= 0
        ? fileName.substring(lastSlash + 1)
        : fileName;

    final dot = name.lastIndexOf('.');

    if (dot > 0) {
      return name.substring(0, dot);
    }

    return name;
  }
}