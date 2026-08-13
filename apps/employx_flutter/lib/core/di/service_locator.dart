import 'package:get_it/get_it.dart';

import '../api/api_client.dart';
import '../actions/command_actions.dart';
import '../actions/mission_actions.dart';
import '../actions/system_actions.dart';
import '../providers/mission_provider.dart';
import '../providers/profile_hub_provider.dart';
import '../providers/upload_provider.dart';
import '../repositories/command_repository.dart';
import '../repositories/cv_repository.dart';
import '../repositories/mission_repository.dart';
import '../repositories/profile_repository.dart';

final sl = GetIt.instance;

void setupServiceLocator() {
  sl.registerLazySingleton<ApiClient>(() => ApiClient());

  sl.registerLazySingleton<MissionRepository>(
    () => MissionRepository(sl()),
  );
  sl.registerLazySingleton<CommandRepository>(
    () => CommandRepository(sl()),
  );
  sl.registerLazySingleton<CVRepository>(
    () => CVRepository(),
  );
  sl.registerLazySingleton<ProfileRepository>(
    () => ProfileRepository(),
  );

  sl.registerLazySingleton<MissionActions>(
    () => MissionActions(
      sl<MissionRepository>(),
      cvRepository: sl<CVRepository>(),
      profileRepository: sl<ProfileRepository>(),
    ),
  );
  sl.registerLazySingleton<CommandActions>(
    () => CommandActions(sl()),
  );
  sl.registerLazySingleton<SystemActions>(
    () => SystemActions(),
  );
  sl.registerLazySingleton<MissionProvider>(
    () => MissionProvider(),
  );
  sl.registerLazySingleton<UploadProvider>(
    () => UploadProvider(),
  );
  sl.registerLazySingleton<ProfileHubProvider>(
    () => ProfileHubProvider(
      sl<MissionRepository>(),
      sl<ProfileRepository>(),
    ),
  );
}
