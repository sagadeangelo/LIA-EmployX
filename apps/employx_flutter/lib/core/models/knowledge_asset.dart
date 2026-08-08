class KnowledgeAsset {
  final String id;
  final String title;
  final String type; // CV, Cover Letter, LinkedIn, Certificate, Portfolio, Document
  final String? content;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  KnowledgeAsset({
    required this.id,
    required this.title,
    required this.type,
    this.content,
    this.metadata,
    required this.createdAt,
    required this.updatedAt,
  });

  factory KnowledgeAsset.fromJson(Map<String, dynamic> json) {
    return KnowledgeAsset(
      id: json['id'] as String,
      title: json['title'] as String,
      type: json['type'] as String,
      content: json['content'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}
