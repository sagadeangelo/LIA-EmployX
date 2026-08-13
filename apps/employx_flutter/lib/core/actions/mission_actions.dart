import 'dart:async';

import 'package:flutter/foundation.dart';

import '../api/api_client.dart';
import '../models/mission_model.dart';
import '../models/professional_profile_model.dart';
import '../models/upload_mission_response.dart';
import '../repositories/cv_repository.dart';
import '../repositories/mission_repository.dart';
import '../repositories/profile_repository.dart';
import '../utils/app_logger.dart';

class MissionActions extends ChangeNotifier {
  final MissionRepository _missionRepository;
  final CVRepository _cvRepository;
  final ProfileRepository _profileRepository;

  MissionModel? _currentMission;
  ProfessionalProfile? _currentProfile;

  bool _isLoading = false;
  String? _error;

  Timer? _pollTimer;

  MissionActions(
    this._missionRepository, {
    CVRepository? cvRepository,
    ProfileRepository? profileRepository,
  })  : _cvRepository = cvRepository ?? CVRepository(),
        _profileRepository = profileRepository ?? ProfileRepository();

  MissionModel? get currentMission => _currentMission;
  ProfessionalProfile? get currentProfile => _currentProfile;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMission => _currentMission != null;

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

  void _setLoading(bool value) {
    if (_isLoading == value) return;
    _isLoading = value;
    notifyListeners();
  }

  Future<void> loadActiveMission({bool silent = false}) async {
    if (!silent) _setLoading(true);

    try {
      final missions = await _missionRepository.getActiveMissions();

      if (missions.isNotEmpty) {
        _currentMission = missions.first;
        final profileId = _currentMission?.profileId;

        if (profileId != null && profileId.isNotEmpty) {
          _currentProfile = await _profileRepository.getProfile(profileId);
        } else {
          _currentProfile = null;
        }
      } else {
        _currentMission = null;
        _currentProfile = null;
      }

      _error = null;
    } catch (e) {
      if (!silent) _error = e.toString();
      AppLogger.error(
        'Mission',
        'Error cargando misión activa',
        error: e,
      );
    } finally {
      if (!silent) _setLoading(false);
    }
  }

  Future<void> createMission(Map<String, dynamic> data) async {
    _setLoading(true);

    try {
      AppLogger.info('Mission', 'Creando nueva misión...');
      _currentMission = await _missionRepository.createMission(data);
      _error = null;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<bool> pingServer() async {
    return ApiClient().ping();
  }

  Future<UploadMissionResponse> uploadCV(
    String filePath,
    String fileName, {
    List<int>? fileBytes,
    String? missionId,
    void Function(int sent, int total)? onSendProgress,
  }) async {
    _setLoading(true);
    final startTime = DateTime.now();

    try {
      AppLogger.info(
        'Mission',
        'Iniciando upload de CV al backend...',
        missionId: missionId,
      );

      final response = await _cvRepository.uploadCV(
        filePath,
        fileName,
        fileBytes: fileBytes,
        missionId: missionId,
        onSendProgress: onSendProgress,
      );

      final durationMs = DateTime.now().difference(startTime).inMilliseconds;
      final mission = response.snapshot.mission;

      _currentMission = mission;
      _currentProfile = response.cv;
      _error = null;
      notifyListeners();

      AppLogger.info(
        'Mission',
        'CV recibido y perfil profesional cargado.',
        missionId: mission.id,
        durationMs: durationMs,
      );

      return response;
    } catch (e) {
      final durationMs = DateTime.now().difference(startTime).inMilliseconds;

      AppLogger.error(
        'Mission',
        'Fallo general al subir CV',
        missionId: missionId,
        durationMs: durationMs,
        error: e,
      );

      _error = e.toString();
      notifyListeners();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> resumeMission() async {
    final mission = _currentMission;
    if (mission == null) return;
    await _missionRepository.resumeMission(mission.id);
  }

  Future<void> restartMission() async {
    final mission = _currentMission;
    if (mission == null) return;
    await _missionRepository.restartMission(mission.id);
  }

  void startPolling() {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(
      const Duration(seconds: 5),
      (_) => loadActiveMission(silent: true),
    );
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
