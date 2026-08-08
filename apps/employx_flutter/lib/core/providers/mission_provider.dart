import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/mission_snapshot_model.dart';
import '../api/api_client.dart';
import '../di/service_locator.dart';
import '../utils/app_logger.dart';

class MissionProvider extends ChangeNotifier {
  final ApiClient _apiClient = sl<ApiClient>();
  
  MissionSnapshotModel? _snapshot;
  bool _isLoading = false;
  String? _error;
  Timer? _pollingTimer;
  
  MissionSnapshotModel? get snapshot => _snapshot;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Inicia el monitoreo, opcionalmente recibiendo un snapshot inicial
  void startMonitoring(String missionId, {MissionSnapshotModel? initialSnapshot}) {
    if (initialSnapshot != null) {
      _snapshot = initialSnapshot;
      notifyListeners();
    }
    
    _scheduleNextPoll(missionId);
    AppLogger.info('MissionProvider', 'Iniciando monitoreo dinámico de Mission: $missionId');
  }

  void _scheduleNextPoll(String missionId) {
    _pollingTimer?.cancel();

    if (_snapshot == null) {
      _fetchSnapshot(missionId);
      return;
    }

    final status = _snapshot!.mission.status;
    int seconds = 2; // default

    if (status == 'RUNNING' || status == 'CREATED') {
      seconds = 1;
    } else if (status == 'WAITING_AGENT') {
      seconds = 2;
    } else if (status == 'COMPLETED' || status == 'FAILED' || status == 'CANCELLED') {
      stopMonitoring();
      return;
    }

    _pollingTimer = Timer(Duration(seconds: seconds), () {
      _fetchSnapshot(missionId);
    });
  }

  void stopMonitoring() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
    AppLogger.info('MissionProvider', 'Monitoreo detenido');
  }

  int _consecutiveErrors = 0;
  static const int _maxConsecutiveErrors = 5;

  Future<void> _fetchSnapshot(String missionId) async {
    try {
      final response = await _apiClient.get('/missions/$missionId/snapshot');

      if (response.statusCode == 200) {
        _snapshot = MissionSnapshotModel.fromJson(response.data);
        _error = null;
        _consecutiveErrors = 0;

        // Reschedule based on the new state
        _scheduleNextPoll(missionId);
      } else if (response.statusCode == 404) {
        // Mission is gone — stop polling permanently
        AppLogger.info('MissionProvider', 'Mission $missionId not found (404) — stopping poll.');
        stopMonitoring();
      }
    } catch (e) {
      _consecutiveErrors++;
      AppLogger.error('MissionProvider', 'Error obteniendo snapshot (${ _consecutiveErrors}/$_maxConsecutiveErrors): $e');
      _error = e.toString();

      if (_consecutiveErrors >= _maxConsecutiveErrors) {
        AppLogger.error('MissionProvider', 'Demasiados errores consecutivos — deteniendo polling.');
        stopMonitoring();
      } else {
        // Retry with last known state
        _scheduleNextPoll(missionId);
      }
    } finally {
      notifyListeners();
    }
  }

  @override
  void dispose() {
    stopMonitoring();
    super.dispose();
  }
}
