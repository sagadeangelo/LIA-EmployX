class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException({required this.message, this.statusCode, this.data});

  @override
  String toString() {
    return 'ApiException: $message (Status: $statusCode)';
  }
}

class NetworkException extends ApiException {
  NetworkException({String message = 'Network connection error'})
      : super(message: message);
}

class TimeoutException extends ApiException {
  TimeoutException({String message = 'Request timed out'})
      : super(message: message);
}

class UnauthorizedException extends ApiException {
  UnauthorizedException({String message = 'Unauthorized access'})
      : super(message: message, statusCode: 401);
}

class ServerException extends ApiException {
  ServerException({String message = 'Internal server error'})
      : super(message: message, statusCode: 500);
}
