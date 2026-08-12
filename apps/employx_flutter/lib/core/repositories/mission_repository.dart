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

  Future<List<MissionModel>> getActiveMissions() async {
    final response = await _apiClient.get('/missions');
    final List<dynamic> data = response.data;
    return data.map((json) => MissionModel.fromJson(json)).toList();
  }

  Future<MissionModel> updateMission(String id, Map<String, dynamic> data) async {
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
