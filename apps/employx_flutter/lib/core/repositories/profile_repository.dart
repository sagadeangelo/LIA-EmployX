import 'package:dio/dio.dart';
import '../models/professional_profile_model.dart';
import '../api/api_client.dart';
import '../utils/app_logger.dart';

class ProfileRepository {
  final ApiClient _apiClient = ApiClient();

  Future<ProfessionalProfile?> getProfile(String profileId) async {
    try {
      final response = await _apiClient.get('/api/v1/profile/$profileId');
      
      if (response.statusCode == 200) {
        return ProfessionalProfile.fromJson(response.data);
      }
      return null;
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        AppLogger.info('ProfileRepository', 'Profile $profileId not found.');
        return null;
      }
      AppLogger.error('ProfileRepository', 'Error fetching profile: ${e.message}', error: e);
      rethrow;
    } catch (e) {
      AppLogger.error('ProfileRepository', 'Unexpected error fetching profile: $e', error: e);
      rethrow;
    }
  }
}
