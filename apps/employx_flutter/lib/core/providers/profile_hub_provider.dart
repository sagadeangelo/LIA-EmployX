import 'dart:async';

import 'package:flutter/foundation.dart';

import '../models/mission_model.dart';
import '../models/professional_profile_model.dart';
import '../repositories/mission_repository.dart';
import '../repositories/profile_repository.dart';
import '../utils/app_logger.dart';

class ProfileHubProvider extends ChangeNotifier {
  final MissionRepository _missionRepository;
  final ProfileRepository _profileRepository;

  final List<ProfessionalProfile> _profiles = [];
  bool _isLoading = false;
  String? _error;
  String? _activeProfileId;

  ProfileHubProvider(
    this._missionRepository,
    this._profileRepository,
  ) {
    unawaited(initialize());
  }

  List<ProfessionalProfile> get profiles => List.unmodifiable(_profiles);
  bool get isLoading => _isLoading;
  String? get error => _error;
  String? get activeProfileId => _activeProfileId;

  ProfessionalProfile? get activeProfile {
    final id = _activeProfileId;
    if (id == null) return _profiles.isEmpty ? null : _profiles.first;

    for (final profile in _profiles) {
      if (profile.id == id) return profile;
    }
    return _profiles.isEmpty ? null : _profiles.first;
  }

  Future<void> initialize() async {
    if (_isLoading) return;

    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final missions = await _missionRepository.getAllMissions();

      final profileIds = <String>{};
      for (final mission in missions) {
        final profileId = mission.profileId;
        if (profileId != null && profileId.isNotEmpty) {
          profileIds.add(profileId);
        }
      }

      final loaded = await Future.wait(
        profileIds.map(_profileRepository.getProfile),
      );

      _profiles
        ..clear()
        ..addAll(
          loaded.whereType<ProfessionalProfile>(),
        );

      _sortProfiles(missions);

      if (_profiles.isNotEmpty) {
        _activeProfileId ??= _profiles.first.id;
      } else {
        _activeProfileId = null;
      }
    } catch (e) {
      _error = e.toString();
      AppLogger.error(
        'ProfileHub',
        'Error hidratando perfiles persistidos',
        error: e,
      );
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> refresh() => initialize();

  void setActiveProfile(String profileId) {
    if (!_profiles.any((profile) => profile.id == profileId)) return;
    _activeProfileId = profileId;
    notifyListeners();
  }

  void upsert(ProfessionalProfile profile) {
    final index = _profiles.indexWhere((item) => item.id == profile.id);
    if (index >= 0) {
      _profiles[index] = profile;
    } else {
      _profiles.insert(0, profile);
    }

    _activeProfileId ??= profile.id;
    notifyListeners();
  }

  void _sortProfiles(List<MissionModel> missions) {
    final missionOrder = <String, DateTime>{};

    for (final mission in missions) {
      final profileId = mission.profileId;
      if (profileId == null || profileId.isEmpty) continue;

      final existing = missionOrder[profileId];
      if (existing == null || mission.updatedAt.isAfter(existing)) {
        missionOrder[profileId] = mission.updatedAt;
      }
    }

    _profiles.sort((a, b) {
      final aDate = missionOrder[a.id] ?? DateTime.fromMillisecondsSinceEpoch(0);
      final bDate = missionOrder[b.id] ?? DateTime.fromMillisecondsSinceEpoch(0);
      return bDate.compareTo(aDate);
    });
  }
}
