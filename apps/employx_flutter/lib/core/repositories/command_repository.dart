import '../api/api_client.dart';
import '../models/command_center_data.dart';

class CommandRepository {
  final ApiClient _apiClient;

  CommandRepository(this._apiClient);

  Future<CommandCenterData> getCommandCenterData(String missionId) async {
    final response = await _apiClient.get('/command-center/$missionId');
    return CommandCenterData.fromJson(response.data);
  }

  Future<void> sendCommand(String missionId, String commandText) async {
    await _apiClient.post('/command-center/$missionId/execute', data: {
      'command': commandText,
    });
  }
}
