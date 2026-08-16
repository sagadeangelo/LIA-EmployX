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

import '../../features/profile/models/cv_document.dart';
import '../../features/profile/providers/profile_hub_provider.dart';

class MissionActions extends ChangeNotifier {
  final MissionRepository _missionRepository;
  final CVRepository _cvRepository;
  final ProfileRepository _profileRepository;
  final ProfileHubProvider _profileHubProvider;

  MissionModel? _currentMission;
  ProfessionalProfile? _currentProfile;

  bool _isLoading = false;
  String? _error;

  Timer? _pollTimer;

  MissionActions(
    this._missionRepository, {
    CVRepository? cvRepository,
    ProfileRepository? profileRepository,
    required ProfileHubProvider profileHubProvider,
  })  : _cvRepository = cvRepository ?? CVRepository(),
        _profileRepository =
            profileRepository ?? ProfileRepository(),
        _profileHubProvider = profileHubProvider;

  // ============================================================
  // GETTERS
  // ============================================================

  MissionModel? get currentMission => _currentMission;

  ProfessionalProfile? get currentProfile => _currentProfile;

  bool get isLoading => _isLoading;

  String? get error => _error;

  bool get hasMission {
    if (_currentMission == null) return false;
    final status = _currentMission!.status;
    return status != 'COMPLETED' && status != 'FAILED' && status != 'CANCELLED';
  }

  bool get hasProfile => _currentProfile != null;

  // ============================================================
  // MISSION STATE
  // ============================================================

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
    if (_isLoading == value) {
      return;
    }

    _isLoading = value;
    notifyListeners();
  }

  // ============================================================
  // LOAD ACTIVE MISSION
  // ============================================================

  Future<void> loadActiveMission({
    bool silent = false,
  }) async {
    if (!silent) {
      _setLoading(true);
    }

    try {
      final missions =
          await _missionRepository.getActiveMissions();

      // Ensure we only pick truly active missions, ignoring terminal states
      // even if the backend accidentally returned them.
      final activeMissions = missions.where((m) =>
        m.status != 'COMPLETED' &&
        m.status != 'FAILED' &&
        m.status != 'CANCELLED'
      ).toList();

      if (activeMissions.isNotEmpty) {
        _currentMission = activeMissions.first;

        final profileId =
            _currentMission?.profileId?.trim();

        if (profileId != null &&
            profileId.isNotEmpty) {
          _currentProfile =
              await _profileRepository.getProfile(
            profileId,
          );
        } else {
          _currentProfile = null;
        }
      } else {
        _currentMission = null;
        _currentProfile = null;
      }

      _error = null;
    } catch (e) {
      if (!silent) {
        _error = e.toString();
      }

      AppLogger.error(
        'Mission',
        'Error cargando misión activa',
        error: e,
      );
    } finally {
      if (!silent) {
        _setLoading(false);
      }
    }
  }

  // ============================================================
  // LOAD PROFILE FOR CV
  // ============================================================

  /// Carga el ProfessionalProfile asociado directamente
  /// al CV seleccionado.
  Future<void> loadProfileForCv(
    CVDocument cv,
  ) async {
    final profileId =
        cv.professionalProfileId?.trim();

    if (profileId == null ||
        profileId.isEmpty) {
      AppLogger.warning(
        'Profile',
        'El CV seleccionado no tiene professionalProfileId.',
      );

      _currentProfile = null;
      _error = null;

      notifyListeners();
      return;
    }

    _setLoading(true);

    try {
      AppLogger.info(
        'Profile',
        'Cargando perfil profesional asociado al CV [$profileId].',
      );

      final profile =
          await _profileRepository.getProfile(
        profileId,
      );

      if (profile == null) {
        AppLogger.warning(
          'Profile',
          'No se encontró ProfessionalProfile [$profileId].',
        );
      } else {
        AppLogger.info(
          'Profile',
          'ProfessionalProfile [$profileId] cargado correctamente.',
        );
      }

      _currentProfile = profile;
      _error = null;

      notifyListeners();
    } catch (e) {
      _currentProfile = null;
      _error = e.toString();

      AppLogger.error(
        'Profile',
        'Error cargando perfil profesional del CV.',
        error: e,
      );

      notifyListeners();

      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  // ============================================================
  // LOAD ACTIVE CV PROFILE
  // ============================================================

  /// Sincroniza ProfessionalProfile con el CV actualmente
  /// seleccionado en ProfileHub.
  Future<void> loadActiveCvProfile() async {
    final activeCv =
        _profileHubProvider.activeCv;

    if (activeCv == null) {
      AppLogger.info(
        'Profile',
        'No existe un CV activo en ProfileHub.',
      );

      _currentProfile = null;
      _error = null;

      notifyListeners();
      return;
    }

    await loadProfileForCv(
      activeCv,
    );
  }

  // ============================================================
  // REFRESH PROFILE AFTER MISSION
  // ============================================================

  /// Refresca el ProfessionalProfile después de que los agentes
  /// terminan una misión.
  ///
  /// El backend procesa los agentes de forma asíncrona, por lo que
  /// el perfil cargado inmediatamente después del upload puede
  /// contener todavía valores provisionales (por ejemplo, métricas 0).
  ///
  /// Aquí hacemos una nueva lectura desde backend y sincronizamos
  /// también el ProfileHub, manteniendo una única fuente de verdad.
  Future<void> refreshProfileAfterMission() async {
    try {
      AppLogger.info(
        'Profile',
        'Refrescando ProfessionalProfile después de completar la misión.',
      );

      await _profileHubProvider.refreshActiveProfessionalProfile();

      final refreshedProfile =
          _profileHubProvider.activeProfessionalProfile;

      if (refreshedProfile != null) {
        _currentProfile = refreshedProfile;
        _error = null;

        AppLogger.info(
          'Profile',
          'ProfessionalProfile actualizado después de la misión.',
        );

        notifyListeners();
        return;
      }

      // Fallback: si ProfileHub no pudo resolver el perfil activo,
      // intentamos cargarlo directamente desde el CV activo.
      await loadActiveCvProfile();
    } catch (e) {
      _error = e.toString();

      AppLogger.error(
        'Profile',
        'Error refrescando ProfessionalProfile después de la misión.',
        error: e,
      );

      notifyListeners();
    }
  }

  // ============================================================
  // CREATE MISSION
  // ============================================================

  Future<void> createMission(
    Map<String, dynamic> data,
  ) async {
    _setLoading(true);

    try {
      AppLogger.info(
        'Mission',
        'Creando nueva misión...',
      );

      _currentMission =
          await _missionRepository.createMission(
        data,
      );

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

  // ============================================================
  // PING
  // ============================================================

  Future<bool> pingServer() async {
    final client = ApiClient();

    return client.ping();
  }

  // ============================================================
  // UPLOAD CV
  // ============================================================

  Future<UploadMissionResponse> uploadCV({
    String? filePath,
    List<int>? fileBytes,
    required String fileName,
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

      final response =
          await _cvRepository.uploadCV(
        filePath: filePath,
        fileBytes: fileBytes,
        fileName: fileName,
        missionId: missionId,
        onSendProgress: onSendProgress,
      );

      final durationMs =
          DateTime.now()
              .difference(startTime)
              .inMilliseconds;

      final mission =
          response.snapshot.mission;

      _currentMission = mission;

      final cvDocument = response.cv;

      if (cvDocument == null) {
        throw StateError(
          'El backend procesó el CV pero no devolvió '
          'el CVDocument en UploadMissionResponse.',
        );
      }

      // UploadMissionResponse.profile es la fuente de verdad.
      final profileId = response.profile?.id.trim();

      AppLogger.info(
        'Mission',
        'CVDocument recibido correctamente.',
        missionId: mission.id,
      );

      AppLogger.info(
        'Profile',
        'ProfessionalProfile asociado al CV: '
        '${profileId ?? 'NULL'}',
        missionId: mission.id,
      );

      await _profileHubProvider.registerProcessedCv(
        id: cvDocument.id.isNotEmpty
            ? cvDocument.id
            : _buildCvDocumentId(
                mission,
                fileName,
              ),
        fileName: cvDocument.fileName.isNotEmpty
            ? cvDocument.fileName
            : fileName,
        localPath: filePath,
        remotePath: cvDocument.remotePath,
        professionalProfileId: profileId,
        displayName: cvDocument.displayName,
      );

      if (profileId != null && profileId.isNotEmpty) {
        await loadProfileForCv(
          cvDocument.copyWith(professionalProfileId: profileId),
        );
      } else {
        AppLogger.warning(
          'Profile',
          'El CV recibido no contiene '
          'professionalProfileId en la respuesta (profile.id). '
          'No se puede cargar el perfil profesional.',
          missionId: mission.id,
        );

        _currentProfile = null;
      }

      _error = null;

      notifyListeners();

      AppLogger.info(
        'Mission',
        'CV recibido, CV registrado y perfil profesional '
        'asociado correctamente.',
        missionId: mission.id,
        durationMs: durationMs,
      );

      return response;
    } catch (e) {
      final durationMs =
          DateTime.now()
              .difference(startTime)
              .inMilliseconds;

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

  // ============================================================
  // CV DOCUMENT ID
  // ============================================================

  String _buildCvDocumentId(
    MissionModel mission,
    String fileName,
  ) {
    final missionId =
        mission.id.trim();

    final normalizedFileName =
        fileName.trim();

    if (missionId.isNotEmpty) {
      return 'cv-$missionId';
    }

    if (normalizedFileName.isNotEmpty) {
      return 'cv-$normalizedFileName';
    }

    return 'cv-${DateTime.now().millisecondsSinceEpoch}';
  }

  // ============================================================
  // RESUME / RESTART
  // ============================================================

  Future<void> resumeMission() async {
    final mission = _currentMission;

    if (mission == null) {
      return;
    }

    await _missionRepository.resumeMission(
      mission.id,
    );
  }

  Future<void> restartMission() async {
    final mission = _currentMission;

    if (mission == null) {
      return;
    }

    await _missionRepository.restartMission(
      mission.id,
    );
  }

  // ============================================================
  // POLLING
  // ============================================================

  void startPolling() {
    _pollTimer?.cancel();

    _pollTimer = Timer.periodic(
      const Duration(seconds: 5),
      (_) {
        loadActiveMission(
          silent: true,
        );
      },
    );
  }

  void stopPolling() {
    _pollTimer?.cancel();
    _pollTimer = null;
  }

  // ============================================================
  // DISPOSE
  // ============================================================

  @override
  void dispose() {
    stopPolling();
    super.dispose();
  }
}