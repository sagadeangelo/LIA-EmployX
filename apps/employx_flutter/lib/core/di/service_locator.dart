import 'package:get_it/get_it.dart';

import '../api/api_client.dart';

import '../repositories/mission_repository.dart';
import '../repositories/command_repository.dart';
import '../repositories/cv_repository.dart';
import '../repositories/profile_repository.dart';

import '../actions/mission_actions.dart';
import '../actions/command_actions.dart';
import '../actions/system_actions.dart';

import '../providers/mission_provider.dart';
import '../providers/upload_provider.dart';

import '../../features/profile/providers/profile_hub_provider.dart';

final sl = GetIt.instance;

void setupServiceLocator() {
  // ============================================================
  // CORE
  // ============================================================

  sl.registerLazySingleton<ApiClient>(
    () => ApiClient(),
  );

  // ============================================================
  // REPOSITORIES
  // ============================================================

  sl.registerLazySingleton<MissionRepository>(
    () => MissionRepository(
      sl<ApiClient>(),
    ),
  );

  sl.registerLazySingleton<CommandRepository>(
    () => CommandRepository(
      sl<ApiClient>(),
    ),
  );

  sl.registerLazySingleton<CVRepository>(
    () => CVRepository(
      apiClient: sl<ApiClient>(),
    ),
  );

  // ------------------------------------------------------------
  // PROFILE REPOSITORY
  // ------------------------------------------------------------

  sl.registerLazySingleton<ProfileRepository>(
    () => ProfileRepository(),
  );

  // ============================================================
  // PROFILE HUB
  // ============================================================

  // UNA ÚNICA INSTANCIA GLOBAL.
  sl.registerLazySingleton<ProfileHubProvider>(
    () => ProfileHubProvider(
      profileRepository: sl<ProfileRepository>(),
    ),
  );

  // ============================================================
  // ACTIONS
  // ============================================================

  sl.registerLazySingleton<MissionActions>(
    () => MissionActions(
      sl<MissionRepository>(),
      cvRepository: sl<CVRepository>(),
      profileRepository: sl<ProfileRepository>(),
      profileHubProvider: sl<ProfileHubProvider>(),
    ),
  );

  sl.registerLazySingleton<CommandActions>(
    () => CommandActions(
      sl<CommandRepository>(),
    ),
  );

  sl.registerLazySingleton<SystemActions>(
    () => SystemActions(),
  );

  // ============================================================
  // PROVIDERS
  // ============================================================

  sl.registerLazySingleton<MissionProvider>(
    () => MissionProvider(
      apiClient: sl<ApiClient>(),
      onMissionCompleted: () =>
          sl<MissionActions>().refreshProfileAfterMission(),
    ),
  );

  sl.registerLazySingleton<UploadProvider>(
    () => UploadProvider(),
  );
}