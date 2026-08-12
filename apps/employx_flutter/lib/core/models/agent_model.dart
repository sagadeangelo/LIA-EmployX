class AgentModel {
  final String id;
  final String name;
  final String role;
  final String description;
  final List<String> capabilities;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;

  AgentModel({
    required this.id,
    required this.name,
    required this.role,
    required this.description,
    this.capabilities = const [],
    this.status = 'idle',
    required this.createdAt,
    required this.updatedAt,
  });

  factory AgentModel.fromJson(Map<String, dynamic> json) {
    return AgentModel(
      id: json['id'] as String,
      name: json['name'] as String,
      role: json['role'] as String,
      description: json['description'] as String,
      capabilities: (json['capabilities'] as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      status: json['status'] as String? ?? 'idle',
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}
