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

  /// Inicia el monitoreo de una misión.
  ///
  /// Si no existe un snapshot en memoria, restaura inmediatamente
  /// el snapshot persistido desde backend. Esto es especialmente
  /// importante después de un refresh del navegador, porque el
  /// Provider de Flutter vuelve a crearse vacío.
  void startMonitoring(
    String missionId, {
    MissionSnapshotModel? initialSnapshot,
  }) {
    _completedMissionId = null;

    if (initialSnapshot != null) {
      _snapshot = initialSnapshot;
      _error = null;
      notifyListeners();
      _scheduleNextPoll(missionId);
      return;
    }

    // Restauración explícita desde backend. No dependemos del estado
    // anterior del Provider ni de datos almacenados únicamente en memoria.
    restorePersistedMission(missionId);

    AppLogger.info(
      'MissionProvider',
      'Iniciando monitoreo dinámico de Mission: $missionId',
    );
  }

  /// Restaura una misión persistida desde backend y reconstruye el
  /// snapshot que consume directamente el Command Center.
  ///
  /// Este método es la ruta de recuperación utilizada después de un
  /// browser refresh. La misión puede estar COMPLETED; en ese caso se
  /// conserva el snapshot y se sincroniza el ProfessionalProfile.
  Future<void> restorePersistedMission(String missionId) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      AppLogger.info(
        'MissionProvider',
        'Restaurando Mission persistida: $missionId',
      );

      final response = await _apiClient.get(
        '/missions/$missionId/snapshot',
      );

      if (response.statusCode == 200) {
        _snapshot = MissionSnapshotModel.fromJson(response.data);
        _error = null;
        _consecutiveErrors = 0;

        AppLogger.info(
          'MissionProvider',
          'Snapshot persistido restaurado: $missionId '
          '(status=${_snapshot!.mission.status})',
        );

        if (_snapshot!.mission.status == 'COMPLETED') {
          await _refreshProfileAfterCompletion(missionId);
        } else if (_snapshot!.mission.status == 'FAILED' ||
            _snapshot!.mission.status == 'CANCELLED') {
          stopMonitoring();
        } else {
          _scheduleNextPoll(missionId);
        }
      } else if (response.statusCode == 404) {
        _error = 'Mission $missionId no encontrada en backend.';
        stopMonitoring();

        AppLogger.warning(
          'MissionProvider',
          'Mission persistida no encontrada (404): $missionId',
        );
      } else {
        _error =
            'No se pudo restaurar la Mission. HTTP ${response.statusCode}';
        _scheduleNextPoll(missionId);
      }
    } catch (e) {
      _consecutiveErrors++;
      _error = e.toString();

      AppLogger.error(
        'MissionProvider',
        'Error restaurando Mission persistida '
        '(${_consecutiveErrors}/$_maxConsecutiveErrors): $e',
      );

      if (_consecutiveErrors < _maxConsecutiveErrors) {
        _scheduleNextPoll(missionId);
      } else {
        stopMonitoring();
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void _scheduleNextPoll(String missionId) {
    _pollingTimer?.cancel();

    if (_snapshot == null) {
      restorePersistedMission(missionId);
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

        if (_snapshot!.mission.status == 'COMPLETED') {
          await _refreshProfileAfterCompletion(missionId);
        } else {
          _scheduleNextPoll(missionId);
        }
      } else if (response.statusCode == 404) {
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
