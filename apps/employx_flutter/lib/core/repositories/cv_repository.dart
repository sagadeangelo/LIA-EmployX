import 'package:dio/dio.dart';
import 'package:http_parser/http_parser.dart';
import '../utils/app_logger.dart';
import '../models/upload_mission_response.dart';

class CVRepository {
  final Dio _dio = Dio(BaseOptions(
    baseUrl: 'http://127.0.0.1:8000', // Adjust baseUrl based on env
    headers: {
      'Accept': 'application/json', // Swagger envía esto
    }
  )); 

  Future<UploadMissionResponse> uploadCV(String filePath, String fileName, {String? missionId, void Function(int, int)? onSendProgress}) async {
    final startTime = DateTime.now();
    AppLogger.info('Repository', 'Preparando archivo para subida...', missionId: missionId);
    
    // Asignar el MediaType genérico (Swagger suele enviar el mime real, octet-stream o pdf)
    // Para igualar a swagger que infiere el tipo por el archivo, usamos explícitamente application/pdf (asumiendo que es CV)
    final multipartFile = await MultipartFile.fromFile(
      filePath, 
      filename: fileName,
      contentType: MediaType('application', 'pdf')
    );
    
    FormData formData = FormData.fromMap({
      "file": multipartFile,
      if (missionId != null) "mission_id": missionId,
    });

    AppLogger.info(
      'Repository', 
      'Enviando POST a /api/v1/cv/upload | URL Base: ${_dio.options.baseUrl} | Headers: ${_dio.options.headers} | Archivo: ${multipartFile.filename}',
      missionId: missionId
    );

    try {
      final reqStartTime = DateTime.now();
      
      // LOG INSTRUMENTAL DE LA PETICION (REQUEST)
      AppLogger.info('Repository', '--- INIT FLUTTER REQUEST LOG ---');
      AppLogger.info('Repository', 'POST ${_dio.options.baseUrl}/api/v1/cv/upload');
      AppLogger.info('Repository', 'Headers: ${_dio.options.headers}');
      AppLogger.info('Repository', 'FormData Fields: ${formData.fields}');
      AppLogger.info('Repository', 'FormData Files: ${formData.files.map((e) => '${e.key}: ${e.value.filename} (${e.value.contentType})').toList()}');
      AppLogger.info('Repository', '--- END FLUTTER REQUEST LOG ---');

      final response = await _dio.post(
        '/api/v1/cv/upload', 
        data: formData,
        onSendProgress: onSendProgress,
      );
      final reqDuration = DateTime.now().difference(reqStartTime).inMilliseconds;
      
      AppLogger.info('Repository', 'Respuesta recibida - Status: ${response.statusCode}', missionId: missionId, durationMs: reqDuration);
      
      if (response.statusCode == 200) {
        AppLogger.info('Repository', 'Subida exitosa confirmada por backend', missionId: missionId);
        return UploadMissionResponse.fromJson(response.data);
      } else {
        throw Exception('Failed to upload CV: ${response.statusMessage}');
      }
    } on DioException catch (e) {
      final totalDuration = DateTime.now().difference(startTime).inMilliseconds;
      AppLogger.error('Repository', 'Error en la petición Dio: ${e.message}', missionId: missionId, durationMs: totalDuration);
      
      // LOG INSTRUMENTAL DE LA RESPUESTA (RESPONSE ERROR)
      AppLogger.error('Repository', '--- INIT FLUTTER ERROR RESPONSE LOG ---');
      AppLogger.error('Repository', 'Status Code: ${e.response?.statusCode}');
      AppLogger.error('Repository', 'Headers: ${e.response?.headers}');
      AppLogger.error('Repository', 'Body: ${e.response?.data}');
      AppLogger.error('Repository', '--- END FLUTTER ERROR RESPONSE LOG ---');
      
      rethrow;
    }
  }
}
