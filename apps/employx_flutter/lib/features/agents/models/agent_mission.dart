class AgentMission {
  final String id;
  final String title;
  final String description;
  final List<String> participantAgentIds;
  double progress; // 0.0 to 1.0

  AgentMission({
    required this.id,
    required this.title,
    required this.description,
    required this.participantAgentIds,
    this.progress = 0.0,
  });
}
