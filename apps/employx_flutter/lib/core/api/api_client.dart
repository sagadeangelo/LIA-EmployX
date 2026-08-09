import 'package:dio/dio.dart';

import '../config/env_config.dart';
import 'api_exceptions.dart';
import '../utils/app_logger.dart';

class ApiClient {
  late final Dio _dio;

  ApiClient() {
    _dio = Dio(
      BaseOptions(
        baseUrl: EnvConfig.baseUrl,
        connectTimeout: const Duration(
          milliseconds: EnvConfig.connectTimeout,
        ),
        receiveTimeout: const Duration(
          milliseconds: EnvConfig.receiveTimeout,
        ),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) {
          AppLogger.info(
            'ApiClient',
            'Request: ${options.method} ${options.uri}',
          );

          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (DioException e, handler) {
          return handler.next(
            _handleError(e),
          );
        },
      ),
    );
  }

  DioException _handleError(
    DioException error,
  ) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        throw TimeoutException();

      case DioExceptionType.badResponse:
        final statusCode =
            error.response?.statusCode;

        if (statusCode == 401) {
          throw UnauthorizedException();
        }

        if (statusCode != null &&
            statusCode >= 500) {
          throw ServerException();
        }

        throw ApiException(
          message:
              error.response?.data?['detail'] ??
                  'An error occurred',
          statusCode: statusCode,
          data: error.response?.data,
        );

      case DioExceptionType.connectionError:
        throw NetworkException();

      default:
        throw ApiException(
          message:
              error.message ??
                  'Unknown error occurred',
        );
    }
  }

  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    return _dio.get(
      path,
      queryParameters: queryParameters,
    );
  }

  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    ProgressCallback? onSendProgress,
  }) async {
    return _dio.post(
      path,
      data: data,
      queryParameters: queryParameters,
      onSendProgress: onSendProgress,
    );
  }

  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
  }) async {
    return _dio.put(
      path,
      data: data,
      queryParameters: queryParameters,
    );
  }

  Future<Response> delete(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    return _dio.delete(
      path,
      queryParameters: queryParameters,
    );
  }

  Future<bool> ping() async {
    try {
      final response = await _dio.get('/ping');

      return response.data['ok'] == true;
    } catch (_) {
      return false;
    }
  }
}