import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/mission_model.dart';
import '../repositories/mission_repository.dart';
import '../repositories/cv_repository.dart';
import '../utils/app_logger.dart';
import '../models/upload_mission_response.dart';
import '../models/professional_profile_model.dart';
import '../api/api_client.dart';
import '../repositories/profile_repository.dart';

class MissionActions extends ChangeNotifier {
  final MissionRepository _missionRepository;
  final CVRepository _cvRepository = CVRepository();
  final ProfileRepository _profileRepository = ProfileRepository();

  MissionModel? _currentMission;
  ProfessionalProfile? _currentProfile;
  bool _isLoading = false;
  String? _error;
  Timer? _pollTimer;

  MissionActions(this._missionRepository);

  MissionModel? get currentMission => _currentMission;
  ProfessionalProfile? get currentProfile => _currentProfile;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMission => _currentMission != null;

  /// Detaches the current mission from the active state without deleting it.
  /// The mission remains in the backend history (auditable), but Flutter
  /// treats it as no longer "live". Use before starting a new upload flow.
  void detachCurrentMission() {
    _currentMission = null;
    _currentProfile = null;
    _error = null;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  Future<void> loadActiveMission({bool silent = false}) async {
    if (!silent) _setLoading(true);
    try {
      final missions = await _missionRepository.getActiveMissions();
      if (missions.isNotEmpty) {
        _currentMission = missions.first;
        if (_currentMission?.profileId != null) {
          _currentProfile = await _profileRepository.getProfile(_currentMission!.profileId!);
        }
      } else {
        _currentMission = null;
        _currentProfile = null;
      }
      _error = null;
    } catch (e) {
      if (!silent) _error = e.toString();
    } finally {
      if (!silent) _setLoading(false);
    }
  }

  Future<void> createMission(Map<String, dynamic> data) async {
    _setLoading(true);
    final startTime = DateTime.now();
    try {
      AppLogger.info('Mission', 'Creando nueva misión...');
      _currentMission = await _missionRepository.createMission(data);
      final durationMs = DateTime.now().difference(startTime).inMilliseconds;
      AppLogger.info('Mission', 'Misión creada exitosamente', missionId: _currentMission?.id, durationMs: durationMs);
      _error = null;
    } catch (e) {
      final durationMs = DateTime.now().difference(startTime).inMilliseconds;
      AppLogger.error('Mission', 'Error al crear misión', durationMs: durationMs, error: e);
      _error = e.toString();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  Future<bool> pingServer() async {
    final client = ApiClient();
    return await client.ping();
  }

  Future<UploadMissionResponse> uploadCV(String filePath, String fileName, {void Function(int, int)? onSendProgress}) async {
    _setLoading(true);
    final startTime = DateTime.now();
    try {
      AppLogger.info('Mission', 'Iniciando upload de CV al repository (Backend creará la misión)');
      
      final response = await _cvRepository.uploadCV(
        filePath, 
        fileName, 
        onSendProgress: onSendProgress,
      );
      
      final durationMs = DateTime.now().difference(startTime).inMilliseconds;
      AppLogger.info('Mission', 'Upload completado, Backend retornó Mission ID: ${response.snapshot.mission.id}', missionId: response.snapshot.mission.id, durationMs: durationMs);
      
      // El backend nos devolvió la misión y el snapshot inicial, lo guardamos
      _currentMission = response.snapshot.mission;
      _error = null;
      notifyListeners();
      return response;
      
    } catch (e) {
      final durationMs = DateTime.now().difference(startTime).inMilliseconds;
      AppLogger.error('Mission', 'Fallo general al subir CV', durationMs: durationMs, error: e);
      _error = e.toString();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> resumeMission() async {
    if (_currentMission == null) return;
    try {
      await _missionRepository.resumeMission(_currentMission!.id);
    } catch (e) {
      AppLogger.error('Mission', 'Failed to resume mission: $e');
    }
  }

  Future<void> restartMission() async {
    if (_currentMission == null) return;
    try {
      await _missionRepository.restartMission(_currentMission!.id);
    } catch (e) {
      AppLogger.error('Mission', 'Failed to restart mission: $e');
    }
  }

  void startPolling() {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      loadActiveMission(silent: true);
    });
  }

  void stopPolling() {
    _pollTimer?.cancel();
    _pollTimer = null;
  }

  @override
  void dispose() {
    stopPolling();
    super.dispose();
  }
}
