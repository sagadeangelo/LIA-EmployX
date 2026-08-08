import 'package:employx_flutter/core/models/mission_snapshot_model.dart';

class UploadMissionResponse {
  final MissionSnapshotModel snapshot;

  UploadMissionResponse({
    required this.snapshot,
  });

  factory UploadMissionResponse.fromJson(Map<String, dynamic> json) {
    return UploadMissionResponse(
      snapshot: MissionSnapshotModel.fromJson(json['snapshot']),
    );
  }
}
