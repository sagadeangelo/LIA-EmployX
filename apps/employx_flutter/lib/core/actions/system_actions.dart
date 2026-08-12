import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import '../api/api_client.dart';
import '../di/service_locator.dart';
import '../utils/app_logger.dart';
import '../config/env_config.dart';

class SystemActions extends ChangeNotifier {
  final ApiClient _apiClient = sl<ApiClient>();
  
  bool _isLoading = false;
  String? _error;
  
  int _activeMissions = 0;
  bool _isBackendOnline = false;
  bool _isRuntimeOnline = false;
  bool _isStorageOnline = false;
  bool _isApiOnline = false;
  String _version = "v0.9";

  bool get isLoading => _isLoading;
  String? get error => _error;
  
  int get activeMissions => _activeMissions;
  bool get isBackendOnline => _isBackendOnline;
  bool get isRuntimeOnline => _isRuntimeOnline;
  bool get isStorageOnline => _isStorageOnline;
  bool get isApiOnline => _isApiOnline;
  String get version => _version;

  Timer? _pollingTimer;

  SystemActions() {
    startPolling();
  }

  @override
  void dispose() {
    stopPolling();
    super.dispose();
  }

  void startPolling() {
    if (_pollingTimer != null && _pollingTimer!.isActive) return;
    _fetchHealth();
    _pollingTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _fetchHealth();
    });
  }

  void stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  Future<void> _fetchHealth() async {
    final healthUrl = '${EnvConfig.baseUrl}/health';
    final runtimeUrl = '${EnvConfig.baseUrl}/runtime';
    
    AppLogger.info('SystemActions', 'Comprobando conectividad. GET URL: $healthUrl');
    try {
      final healthResponse = await _apiClient.get('/health');
      
      AppLogger.info('SystemActions', 'Respuesta HTTP /health: Status Code: ${healthResponse.statusCode}');
      AppLogger.debug('SystemActions', 'Response Body /health: ${healthResponse.data}');

      // Si responde el health, el backend y el API están online
      final healthData = healthResponse.data;
      if (healthData['status'] == 'ok') {
        _isBackendOnline = true;
        _isApiOnline = true;
        _isStorageOnline = healthData['storage'] == true;
        // La BD no se expone al UI aún pero se podría agregar
      }

      // Luego consultar runtime
      AppLogger.info('SystemActions', 'Consultando métricas. GET URL: $runtimeUrl');
      final runtimeResponse = await _apiClient.get('/runtime');
      
      AppLogger.info('SystemActions', 'Respuesta HTTP /runtime: Status Code: ${runtimeResponse.statusCode}');
      final runtimeData = runtimeResponse.data;
      
      if (runtimeData['status'] == 'running') {
        _isRuntimeOnline = true;
        _activeMissions = runtimeData['active_missions'] ?? 0;
      }
      
      _error = null;
    } catch (e) {
      if (e is DioException) {
        AppLogger.error('SystemActions', 'Error de conectividad HTTP: ${e.message} | Status Code: ${e.response?.statusCode} | Response Body: ${e.response?.data}');
      } else {
        AppLogger.error('SystemActions', 'Error desconocido al comprobar conectividad: $e');
      }
      
      _isBackendOnline = false;
      _isApiOnline = false;
      _isRuntimeOnline = false;
      _isStorageOnline = false;
      _error = e.toString();
    } finally {
      notifyListeners();
    }
  }
}
