import 'package:employx_flutter/core/models/mission_snapshot_model.dart';
import 'package:employx_flutter/core/models/professional_profile_model.dart';

class UploadMissionResponse {
  final MissionSnapshotModel snapshot;
  final ProfessionalProfile? cv;

  const UploadMissionResponse({
    required this.snapshot,
    this.cv,
  });

  factory UploadMissionResponse.fromJson(
    Map<String, dynamic> json,
  ) {
    final rawSnapshot = json['snapshot'];

    MissionSnapshotModel snapshot;

    if (rawSnapshot is Map<String, dynamic>) {
      snapshot = MissionSnapshotModel.fromJson(rawSnapshot);
    } else if (rawSnapshot is Map) {
      snapshot = MissionSnapshotModel.fromJson(
        Map<String, dynamic>.from(rawSnapshot),
      );
    } else {
      throw FormatException(
        'UploadMissionResponse: missing or invalid snapshot.',
      );
    }

    ProfessionalProfile? cv;

    final rawCv = json['cv'];

    if (rawCv is Map<String, dynamic>) {
      cv = ProfessionalProfile.fromJson(rawCv);
    } else if (rawCv is Map) {
      cv = ProfessionalProfile.fromJson(
        Map<String, dynamic>.from(rawCv),
      );
    }

    return UploadMissionResponse(
      snapshot: snapshot,
      cv: cv,
    );
  }
}