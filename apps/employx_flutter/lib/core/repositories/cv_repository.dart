import 'package:dio/dio.dart';

import '../api/api_client.dart';
import '../models/upload_mission_response.dart';
import '../utils/app_logger.dart';

class CVRepository {
  final ApiClient _apiClient;

  CVRepository({
    ApiClient? apiClient,
  }) : _apiClient = apiClient ?? ApiClient();

  Future<UploadMissionResponse> uploadCV(
    String filePath,
    String fileName, {
    String? missionId,
    void Function(int sent, int total)? onSendProgress,
  }) async {
    final startTime = DateTime.now();

    AppLogger.info(
      'CVRepository',
      'Preparando CV para subida...',
      missionId: missionId,
    );

    final multipartFile =
        await MultipartFile.fromFile(
      filePath,
      filename: fileName,
      contentType: _contentTypeForFile(
        fileName,
      ),
    );

    final formData = FormData.fromMap({
      'file': multipartFile,
      if (missionId != null &&
          missionId.isNotEmpty)
        'mission_id': missionId,
    });

    AppLogger.info(
      'CVRepository',
      'POST /api/v1/cv/upload',
      missionId: missionId,
    );

    AppLogger.info(
      'CVRepository',
      'Archivo: $fileName',
      missionId: missionId,
    );

    try {
      final response =
          await _apiClient.post(
        '/cv/upload',
        data: formData,
        onSendProgress: onSendProgress,
      );

      final durationMs =
          DateTime.now()
              .difference(startTime)
              .inMilliseconds;

      AppLogger.info(
        'CVRepository',
        'Respuesta recibida: ${response.statusCode}',
        missionId: missionId,
        durationMs: durationMs,
      );

      if (response.statusCode != 200) {
        throw Exception(
          'CV upload failed: '
          '${response.statusCode} '
          '${response.statusMessage}',
        );
      }

      if (response.data is! Map) {
        throw Exception(
          'Invalid CV upload response: '
          'expected JSON object.',
        );
      }

      final result =
          UploadMissionResponse.fromJson(
        Map<String, dynamic>.from(
          response.data as Map,
        ),
      );

      AppLogger.info(
        'CVRepository',
        'CV procesado correctamente.',
        missionId: missionId,
        durationMs: durationMs,
      );

      return result;
    } on DioException catch (e) {
      final durationMs =
          DateTime.now()
              .difference(startTime)
              .inMilliseconds;

      AppLogger.error(
        'CVRepository',
        'Error Dio durante upload: ${e.message}',
        missionId: missionId,
        durationMs: durationMs,
        error: e,
      );

      rethrow;
    } catch (e) {
      final durationMs =
          DateTime.now()
              .difference(startTime)
              .inMilliseconds;

      AppLogger.error(
        'CVRepository',
        'Error procesando respuesta del CV: $e',
        missionId: missionId,
        durationMs: durationMs,
        error: e,
      );

      rethrow;
    }
  }

  DioMediaType _contentTypeForFile(
    String fileName,
  ) {
    final extension =
        fileName.toLowerCase().split('.').last;

    switch (extension) {
      case 'pdf':
        return DioMediaType(
          'application',
          'pdf',
        );

      case 'docx':
        return DioMediaType(
          'application',
          'vnd.openxmlformats-officedocument.wordprocessingml.document',
        );

      case 'doc':
        return DioMediaType(
          'application',
          'msword',
        );

      case 'txt':
        return DioMediaType(
          'text',
          'plain',
        );

      default:
        return DioMediaType(
          'application',
          'octet-stream',
        );
    }
  }
}
