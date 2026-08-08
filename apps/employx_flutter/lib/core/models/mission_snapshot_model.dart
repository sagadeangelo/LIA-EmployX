import 'mission_model.dart';
import 'mission_event_model.dart';

class RuntimeStatusModel {
  final bool online;
  final List<String> activeAgents;
  final String? currentAgent;

  RuntimeStatusModel({
    required this.online,
    required this.activeAgents,
    this.currentAgent,
  });

  factory RuntimeStatusModel.fromJson(Map<String, dynamic> json) {
    return RuntimeStatusModel(
      online: json['online'] ?? false,
      activeAgents: (json['active_agents'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      currentAgent: json['current_agent'] as String?,
    );
  }
}

class SystemHealthModel {
  final String status;
  final bool database;
  final bool storage;
  final String version;

  SystemHealthModel({
    required this.status,
    required this.database,
    required this.storage,
    required this.version,
  });

  factory SystemHealthModel.fromJson(Map<String, dynamic> json) {
    return SystemHealthModel(
      status: json['status'] ?? 'unknown',
      database: json['database'] ?? false,
      storage: json['storage'] ?? false,
      version: json['version'] ?? 'unknown',
    );
  }
}

class MissionSnapshotModel {
  final MissionModel mission;
  final RuntimeStatusModel runtime;
  final List<MissionEventModel> timeline;
  final int progress;
  final String currentStep;
  final Map<String, dynamic> results;
  final SystemHealthModel health;
  final List<String> warnings;
  final List<String> errors;
  final List<String> availableActions;
  /// Tells Flutter *how* to retry a failed mission.
  /// 'UPLOAD_REQUIRED' | 'RESUME_ALLOWED' | 'NONE'
  final String retryMode;

  MissionSnapshotModel({
    required this.mission,
    required this.runtime,
    required this.timeline,
    required this.progress,
    required this.currentStep,
    required this.results,
    required this.health,
    required this.warnings,
    required this.errors,
    this.availableActions = const [],
    this.retryMode = 'NONE',
  });

  factory MissionSnapshotModel.fromJson(Map<String, dynamic> json) {
    return MissionSnapshotModel(
      mission: MissionModel.fromJson(json['mission'] as Map<String, dynamic>),
      runtime: RuntimeStatusModel.fromJson(json['runtime'] as Map<String, dynamic>),
      timeline: (json['timeline'] as List<dynamic>?)
              ?.map((e) => MissionEventModel.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      progress: json['progress'] ?? 0,
      currentStep: json['current_step'] ?? '',
      results: json['results'] as Map<String, dynamic>? ?? {},
      health: SystemHealthModel.fromJson(json['health'] as Map<String, dynamic>),
      warnings: (json['warnings'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      errors: (json['errors'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      availableActions: (json['availableActions'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      retryMode: json['retryMode'] as String? ?? 'NONE',
    );
  }
}
