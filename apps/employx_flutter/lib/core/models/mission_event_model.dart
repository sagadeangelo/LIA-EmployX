class MissionEventModel {
  final String id;
  final String missionId;
  final DateTime timestamp;
  final String source;
  final String type;
  final String severity;
  final String title;
  final String description;
  final String? stage;
  final String? userMessage;
  final String? developerMessage;
  final String? logs;
  final int duration;
  final Map<String, dynamic> metadata;

  MissionEventModel({
    required this.id,
    required this.missionId,
    required this.timestamp,
    required this.source,
    required this.type,
    required this.severity,
    required this.title,
    required this.description,
    this.stage,
    this.userMessage,
    this.developerMessage,
    this.logs,
    this.duration = 0,
    this.metadata = const {},
  });

  factory MissionEventModel.fromJson(Map<String, dynamic> json) {
    return MissionEventModel(
      id: json['id'] as String,
      missionId: json['mission_id'] as String,
      timestamp: DateTime.parse(json['timestamp']),
      source: json['source'] as String,
      type: json['type'] as String,
      severity: json['severity'] as String? ?? 'info',
      title: json['title'] as String,
      description: json['description'] as String,
      stage: json['stage'] as String?,
      userMessage: json['userMessage'] as String?,
      developerMessage: json['developerMessage'] as String?,
      logs: json['logs'] as String?,
      duration: json['duration'] as int? ?? 0,
      metadata: json['metadata'] as Map<String, dynamic>? ?? {},
    );
  }
}
