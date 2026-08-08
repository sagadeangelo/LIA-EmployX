class MissionModel {
  final String id;
  final String title;
  final String careerGoal;
  
  // OS State Machine
  final String status;
  final String currentStep;
  final int progress;
  final String? failureReason;
  final String? profileId;
  
  // Runtime engine
  final List<String> activeAgents;
  
  // Data Structures
  final Map<String, dynamic> input;
  final Map<String, dynamic> configuration;
  final Map<String, dynamic> context;
  
  final Map<String, dynamic> outputs;
  final Map<String, dynamic> metrics;
  final Map<String, dynamic> artifacts;
  
  final List<String> errors;
  final List<String> warnings;
  
  final DateTime createdAt;
  final DateTime updatedAt;
  final int duration; // In seconds

  MissionModel({
    required this.id,
    required this.title,
    required this.careerGoal,
    required this.status,
    required this.currentStep,
    this.progress = 0,
    this.failureReason,
    this.profileId,
    this.activeAgents = const [],
    this.input = const {},
    this.configuration = const {},
    this.context = const {},
    this.outputs = const {},
    this.metrics = const {},
    this.artifacts = const {},
    this.errors = const [],
    this.warnings = const [],
    required this.createdAt,
    required this.updatedAt,
    this.duration = 0,
  });

  factory MissionModel.fromJson(Map<String, dynamic> json) {
    return MissionModel(
      id: json['id'] as String,
      title: json['title'] as String,
      careerGoal: json['career_goal'] as String,
      status: json['status'] as String,
      currentStep: json['current_step'] as String,
      progress: json['progress'] as int? ?? 0,
      failureReason: json['failureReason'] as String?,
      profileId: json['profile_id'] as String?,
      activeAgents: (json['active_agents'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      input: json['input'] as Map<String, dynamic>? ?? {},
      configuration: json['configuration'] as Map<String, dynamic>? ?? {},
      context: json['context'] as Map<String, dynamic>? ?? {},
      outputs: json['outputs'] as Map<String, dynamic>? ?? {},
      metrics: json['metrics'] as Map<String, dynamic>? ?? {},
      artifacts: json['artifacts'] as Map<String, dynamic>? ?? {},
      errors: (json['errors'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      warnings: (json['warnings'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
      duration: json['duration'] as int? ?? 0,
    );
  }
}
