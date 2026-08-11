class VacancyModel {
  final String id;
  final String title;
  final String company;
  final String location;
  final String modality;
  final String employmentType;
  final String experienceLevel;

  final double? salaryMin;
  final double? salaryMax;
  final String? currency;

  final String description;

  final List<String> skills;

  final String source;
  final String sourceUrl;
  final String? applicationUrl;

  final DateTime? postedAt;

  const VacancyModel({
    required this.id,
    required this.title,
    required this.company,
    this.location = '',
    this.modality = '',
    this.employmentType = '',
    this.experienceLevel = '',
    this.salaryMin,
    this.salaryMax,
    this.currency,
    this.description = '',
    this.skills = const [],
    this.source = '',
    this.sourceUrl = '',
    this.applicationUrl,
    this.postedAt,
  });

  factory VacancyModel.fromJson(Map<String, dynamic> json) {
    return VacancyModel(
      id: _stringValue(json['id']),
      title: _stringValue(json['title']),
      company: _stringValue(json['company']),
      location: _stringValue(json['location']),
      modality: _stringValue(json['modality']),
      employmentType: _stringValue(json['employment_type']),
      experienceLevel: _stringValue(json['experience_level']),
      salaryMin: _doubleValue(json['salary_min']),
      salaryMax: _doubleValue(json['salary_max']),
      currency: _nullableString(json['currency']),
      description: _stringValue(json['description']),
      skills: _stringList(json['skills']),
      source: _stringValue(json['source']),
      sourceUrl: _stringValue(json['source_url']),
      applicationUrl: _nullableString(json['application_url']),
      postedAt: _dateTimeValue(json['posted_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'company': company,
      'location': location,
      'modality': modality,
      'employment_type': employmentType,
      'experience_level': experienceLevel,
      'salary_min': salaryMin,
      'salary_max': salaryMax,
      'currency': currency,
      'description': description,
      'skills': skills,
      'source': source,
      'source_url': sourceUrl,
      'application_url': applicationUrl,
      'posted_at': postedAt?.toIso8601String(),
    };
  }

  VacancyModel copyWith({
    String? id,
    String? title,
    String? company,
    String? location,
    String? modality,
    String? employmentType,
    String? experienceLevel,
    double? salaryMin,
    double? salaryMax,
    String? currency,
    String? description,
    List<String>? skills,
    String? source,
    String? sourceUrl,
    String? applicationUrl,
    DateTime? postedAt,
  }) {
    return VacancyModel(
      id: id ?? this.id,
      title: title ?? this.title,
      company: company ?? this.company,
      location: location ?? this.location,
      modality: modality ?? this.modality,
      employmentType: employmentType ?? this.employmentType,
      experienceLevel: experienceLevel ?? this.experienceLevel,
      salaryMin: salaryMin ?? this.salaryMin,
      salaryMax: salaryMax ?? this.salaryMax,
      currency: currency ?? this.currency,
      description: description ?? this.description,
      skills: skills ?? this.skills,
      source: source ?? this.source,
      sourceUrl: sourceUrl ?? this.sourceUrl,
      applicationUrl: applicationUrl ?? this.applicationUrl,
      postedAt: postedAt ?? this.postedAt,
    );
  }

  static String _stringValue(dynamic value) {
    if (value == null) {
      return '';
    }

    return value.toString().trim();
  }

  static String? _nullableString(dynamic value) {
    final result = _stringValue(value);

    return result.isEmpty ? null : result;
  }

  static double? _doubleValue(dynamic value) {
    if (value == null) {
      return null;
    }

    if (value is num) {
      return value.toDouble();
    }

    return double.tryParse(value.toString());
  }

  static List<String> _stringList(dynamic value) {
    if (value is! List) {
      return const [];
    }

    return value
        .map((item) => item.toString().trim())
        .where((item) => item.isNotEmpty)
        .toList();
  }

  static DateTime? _dateTimeValue(dynamic value) {
    if (value == null) {
      return null;
    }

    return DateTime.tryParse(value.toString());
  }
}