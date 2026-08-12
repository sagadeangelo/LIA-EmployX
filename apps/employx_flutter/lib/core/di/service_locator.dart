import 'package:get_it/get_it.dart';
import '../api/api_client.dart';
import '../repositories/mission_repository.dart';
import '../repositories/command_repository.dart';
import '../actions/mission_actions.dart';
import '../actions/command_actions.dart';
import '../actions/system_actions.dart';
import '../repositories/cv_repository.dart';
import '../providers/mission_provider.dart';
import '../providers/upload_provider.dart';

final sl = GetIt.instance;

void setupServiceLocator() {
  // Core
  sl.registerLazySingleton<ApiClient>(() => ApiClient());

  // Repositories
  sl.registerLazySingleton<MissionRepository>(() => MissionRepository(sl()));
  sl.registerLazySingleton<CommandRepository>(() => CommandRepository(sl()));
  sl.registerLazySingleton<CVRepository>(() => CVRepository());

  // Actions & Providers
  sl.registerLazySingleton<MissionActions>(() => MissionActions(sl<MissionRepository>()));
  sl.registerLazySingleton<CommandActions>(() => CommandActions(sl()));
  sl.registerLazySingleton<SystemActions>(() => SystemActions());
  sl.registerLazySingleton<MissionProvider>(() => MissionProvider());
  sl.registerLazySingleton<UploadProvider>(() => UploadProvider());
}
