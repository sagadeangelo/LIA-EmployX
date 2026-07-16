enum NotificationType {
  info,
  success,
  warning,
  error,
}

class AgentNotification {
  final String id;
  final String agentName;
  final String message;
  final DateTime timestamp;
  final NotificationType type;

  AgentNotification({
    required this.id,
    required this.agentName,
    required this.message,
    required this.timestamp,
    this.type = NotificationType.info,
  });
}
