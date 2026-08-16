import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/mission_snapshot_model.dart';
import '../api/api_client.dart';
import '../utils/app_logger.dart';

class MissionProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  final Future<void> Function()? _onMissionCompleted;

  MissionSnapshotModel? _snapshot;
  bool _isLoading = false;
  String? _error;
  Timer? _pollingTimer;
  String? _completedMissionId;

  MissionProvider({
    ApiClient? apiClient,
    Future<void> Function()? onMissionCompleted,
  })  : _apiClient = apiClient ?? ApiClient(),
        _onMissionCompleted = onMissionCompleted;

  MissionSnapshotModel? get snapshot => _snapshot;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// Inicia el monitoreo, opcionalmente recibiendo un snapshot inicial.
  void startMonitoring(
    String missionId, {
    MissionSnapshotModel? initialSnapshot,
  }) {
    _completedMissionId = null;

    if (initialSnapshot != null) {
      _snapshot = initialSnapshot;
      notifyListeners();
    }

    _scheduleNextPoll(missionId);
    AppLogger.info(
      'MissionProvider',
      'Iniciando monitoreo dinámico de Mission: $missionId',
    );
  }

  void _scheduleNextPoll(String missionId) {
    _pollingTimer?.cancel();

    if (_snapshot == null) {
      _fetchSnapshot(missionId);
      return;
    }

    final status = _snapshot!.mission.status;

    if (status == 'COMPLETED') {
      _refreshProfileAfterCompletion(missionId);
      return;
    }

    if (status == 'FAILED' || status == 'CANCELLED') {
      stopMonitoring();
      return;
    }

    int seconds = 3;

    if (status == 'RUNNING' ||
        status == 'CREATED' ||
        status == 'WAITING_AGENT') {
      seconds = 3;
    }

    if (_consecutiveErrors > 0) {
      // Exponential backoff up to 30 seconds.
      int multiplier = 1 << _consecutiveErrors;
      seconds = seconds * multiplier;
      if (seconds > 30) {
        seconds = 30;
      }
    }

    _pollingTimer = Timer(
      Duration(seconds: seconds),
      () {
        _fetchSnapshot(missionId);
      },
    );
  }

  Future<void> _refreshProfileAfterCompletion(String missionId) async {
    // Evita repetir la recarga si el mismo snapshot COMPLETED
    // vuelve a entrar por una llamada adicional.
    if (_completedMissionId == missionId) {
      stopMonitoring();
      return;
    }

    _completedMissionId = missionId;
    stopMonitoring();

    if (_onMissionCompleted == null) {
      AppLogger.warning(
        'MissionProvider',
        'Misión $missionId completada, pero no hay callback de sincronización de perfil.',
      );
      return;
    }

    try {
      AppLogger.info(
        'MissionProvider',
        'Misión $missionId completada. Refrescando ProfessionalProfile...',
      );

      await _onMissionCompleted!();

      AppLogger.info(
        'MissionProvider',
        'ProfessionalProfile sincronizado después de completar $missionId.',
      );
    } catch (e) {
      _error = e.toString();

      AppLogger.error(
        'MissionProvider',
        'Error sincronizando ProfessionalProfile tras completar $missionId.',
        error: e,
      );
    } finally {
      notifyListeners();
    }
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
      final response = await _apiClient.get(
        '/missions/$missionId/snapshot',
      );

      if (response.statusCode == 200) {
        _snapshot = MissionSnapshotModel.fromJson(response.data);
        _error = null;
        _consecutiveErrors = 0;

        // Si los agentes ya terminaron, sincronizamos el perfil antes
        // de detener definitivamente el monitoreo.
        if (_snapshot!.mission.status == 'COMPLETED') {
          await _refreshProfileAfterCompletion(missionId);
        } else {
          _scheduleNextPoll(missionId);
        }
      } else if (response.statusCode == 404) {
        // Mission is gone — stop polling permanently.
        AppLogger.info(
          'MissionProvider',
          'Mission $missionId not found (404) — stopping poll.',
        );
        stopMonitoring();
      }
    } catch (e) {
      _consecutiveErrors++;
      AppLogger.error(
        'MissionProvider',
        'Error obteniendo snapshot (${_consecutiveErrors}/$_maxConsecutiveErrors): $e',
      );
      _error = e.toString();

      if (_consecutiveErrors >= _maxConsecutiveErrors) {
        AppLogger.error(
          'MissionProvider',
          'Demasiados errores consecutivos — deteniendo polling.',
        );
        stopMonitoring();
      } else {
        // Retry with last known state.
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
