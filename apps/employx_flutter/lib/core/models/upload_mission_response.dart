import 'package:employx_flutter/core/models/mission_snapshot_model.dart';
import 'package:employx_flutter/core/models/professional_profile_model.dart';
import 'package:employx_flutter/features/profile/models/cv_document.dart';

class UploadMissionResponse {
  final MissionSnapshotModel snapshot;
  final CVDocument? cv;
  final ProfessionalProfile? profile;

  const UploadMissionResponse({
    required this.snapshot,
    this.cv,
    this.profile,
  });

  factory UploadMissionResponse.fromJson(
    Map<String, dynamic> json,
  ) {
    // ================================================================
    // SNAPSHOT
    // ================================================================

    final rawSnapshot = json['snapshot'];

    if (rawSnapshot == null) {
      throw FormatException(
        'UploadMissionResponse: falta snapshot.',
      );
    }

    final MissionSnapshotModel snapshot;

    if (rawSnapshot is Map<String, dynamic>) {
      snapshot = MissionSnapshotModel.fromJson(
        rawSnapshot,
      );
    } else if (rawSnapshot is Map) {
      snapshot = MissionSnapshotModel.fromJson(
        Map<String, dynamic>.from(
          rawSnapshot,
        ),
      );
    } else {
      throw FormatException(
        'UploadMissionResponse: snapshot inválido.',
      );
    }

    // ================================================================
    // CV DOCUMENT
    // ================================================================

    CVDocument? cv;

    final rawCv = json['cv'];

    if (rawCv is Map<String, dynamic>) {
      cv = CVDocument.fromJson(
        rawCv,
      );
    } else if (rawCv is Map) {
      cv = CVDocument.fromJson(
        Map<String, dynamic>.from(
          rawCv,
        ),
      );
    }

    // ================================================================
    // PROFESSIONAL PROFILE
    // ================================================================

    ProfessionalProfile? profile;

    final rawProfile = json['profile'];

    if (rawProfile is Map<String, dynamic>) {
      profile = ProfessionalProfile.fromJson(
        rawProfile,
      );
    } else if (rawProfile is Map) {
      profile = ProfessionalProfile.fromJson(
        Map<String, dynamic>.from(
          rawProfile,
        ),
      );
    }

    return UploadMissionResponse(
      snapshot: snapshot,
      cv: cv,
      profile: profile,
    );
  }
}