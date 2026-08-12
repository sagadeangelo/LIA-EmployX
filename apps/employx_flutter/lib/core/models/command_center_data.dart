class ExecutiveReport {
  final String summary;
  final DateTime generatedAt;

  ExecutiveReport({required this.summary, required this.generatedAt});

  factory ExecutiveReport.fromJson(Map<String, dynamic> json) {
    return ExecutiveReport(
      summary: json['summary'] as String,
      generatedAt: DateTime.parse(json['generated_at']),
    );
  }
}

class PriorityItem {
  final String id;
  final String title;
  final String description;
  final String urgency;
  final String status;

  PriorityItem({
    required this.id,
    required this.title,
    required this.description,
    required this.urgency,
    required this.status,
  });

  factory PriorityItem.fromJson(Map<String, dynamic> json) {
    return PriorityItem(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      urgency: json['urgency'] as String,
      status: json['status'] as String,
    );
  }
}

class OpportunityItem {
  final String id;
  final String title;
  final String company;
  final int matchScore;
  final String? url;

  OpportunityItem({
    required this.id,
    required this.title,
    required this.company,
    required this.matchScore,
    this.url,
  });

  factory OpportunityItem.fromJson(Map<String, dynamic> json) {
    return OpportunityItem(
      id: json['id'] as String,
      title: json['title'] as String,
      company: json['company'] as String,
      matchScore: json['match_score'] as int,
      url: json['url'] as String?,
    );
  }
}

class InsightItem {
  final String id;
  final String content;
  final String type;

  InsightItem({
    required this.id,
    required this.content,
    required this.type,
  });

  factory InsightItem.fromJson(Map<String, dynamic> json) {
    return InsightItem(
      id: json['id'] as String,
      content: json['content'] as String,
      type: json['type'] as String,
    );
  }
}

class CommandCenterData {
  final ExecutiveReport? executiveReport;
  final List<PriorityItem> priorities;
  final List<OpportunityItem> opportunities;
  final List<InsightItem> insights;

  CommandCenterData({
    this.executiveReport,
    this.priorities = const [],
    this.opportunities = const [],
    this.insights = const [],
  });

  factory CommandCenterData.fromJson(Map<String, dynamic> json) {
    return CommandCenterData(
      executiveReport: json['executive_report'] != null 
          ? ExecutiveReport.fromJson(json['executive_report']) 
          : null,
      priorities: (json['priorities'] as List<dynamic>?)
              ?.map((e) => PriorityItem.fromJson(e as Map<String, dynamic>))
              .toList() ?? [],
      opportunities: (json['opportunities'] as List<dynamic>?)
              ?.map((e) => OpportunityItem.fromJson(e as Map<String, dynamic>))
              .toList() ?? [],
      insights: (json['insights'] as List<dynamic>?)
              ?.map((e) => InsightItem.fromJson(e as Map<String, dynamic>))
              .toList() ?? [],
    );
  }
}
