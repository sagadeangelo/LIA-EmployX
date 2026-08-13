import '../api/api_client.dart';
import '../models/mission_model.dart';

class MissionRepository {
  final ApiClient _apiClient;

  MissionRepository(this._apiClient);

  Future<MissionModel> createMission(Map<String, dynamic> data) async {
    final response = await _apiClient.post('/missions', data: data);
    return MissionModel.fromJson(response.data);
  }

  Future<MissionModel> getMission(String id) async {
    final response = await _apiClient.get('/missions/$id');
    return MissionModel.fromJson(response.data);
  }

  Future<List<MissionModel>> getAllMissions() async {
    final response = await _apiClient.get('/missions');
    final data = response.data;

    if (data is! List) {
      throw FormatException('GET /missions devolvió una respuesta inválida.');
    }

    return data
        .whereType<Map>()
        .map((json) => MissionModel.fromJson(
              Map<String, dynamic>.from(json),
            ))
        .toList();
  }

  Future<List<MissionModel>> getActiveMissions() async {
    final missions = await getAllMissions();

    const activeStatuses = <String>{
      'STORED',
      'QUEUED',
      'PROCESSING',
      'WAITING_AGENT',
      'PAUSED',
      'RECOVERED',
    };

    return missions
        .where((mission) => activeStatuses.contains(mission.status))
        .toList()
      ..sort(
        (a, b) => b.updatedAt.compareTo(a.updatedAt),
      );
  }

  Future<MissionModel> updateMission(
    String id,
    Map<String, dynamic> data,
  ) async {
    final response = await _apiClient.put('/missions/$id', data: data);
    return MissionModel.fromJson(response.data);
  }

  Future<void> resumeMission(String id) async {
    await _apiClient.post('/missions/$id/resume');
  }

  Future<void> restartMission(String id) async {
    await _apiClient.post('/missions/$id/restart');
  }
}
