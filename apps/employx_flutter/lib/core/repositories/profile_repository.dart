import 'package:dio/dio.dart';

import '../models/professional_profile_model.dart';
import '../api/api_client.dart';
import '../utils/app_logger.dart';

class ProfileRepository {
  final ApiClient _apiClient;

  ProfileRepository({
    ApiClient? apiClient,
  }) : _apiClient = apiClient ?? ApiClient();

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
}