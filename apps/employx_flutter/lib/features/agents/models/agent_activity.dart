enum ActivityType {
  info,
  success,
  warning,
  error,
}

class AgentActivity {
  final String id;
  final String agentId;
  final String agentName;
  final DateTime timestamp;
  final String title;
  final String description;
  final ActivityType type;

  AgentActivity({
    required this.id,
    required this.agentId,
    required this.agentName,
    required this.timestamp,
    required this.title,
    required this.description,
    this.type = ActivityType.info,
  });
}
