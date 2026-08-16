class PersonalInfo {
  final String name;
  final String email;
  final String phone;
  final String location;
  final String linkedin;
  final String portfolio;
  final String website;
  final String professionalSummary;
  final String careerGoal;
  final String currentPosition;
  final int yearsOfExperience;

  const PersonalInfo({
    this.name = '',
    this.email = '',
    this.phone = '',
    this.location = '',
    this.linkedin = '',
    this.portfolio = '',
    this.website = '',
    this.professionalSummary = '',
    this.careerGoal = '',
    this.currentPosition = '',
    this.yearsOfExperience = 0,
  });

  factory PersonalInfo.fromJson(Map<String, dynamic> json) {
    return PersonalInfo(
      name: _string(json['name']),
      email: _string(json['email']),
      phone: _string(json['phone']),
      location: _string(json['location']),
      linkedin: _string(json['linkedin']),
      portfolio: _string(json['portfolio']),
      website: _string(json['website']),
      professionalSummary: _string(
        json['professional_summary'],
      ),
      careerGoal: _string(json['career_goal']),
      currentPosition: _string(
        json['current_position'],
      ),
      yearsOfExperience: _int(
        json['years_of_experience'],
      ),
    );
  }
}

class Experience {
  final String company;
  final String role;
  final String startDate;
  final String endDate;
  final String description;
  final List<String> achievements;
  final List<String> technologies;
  final List<String> skillsUsed;

  const Experience({
    this.company = '',
    this.role = '',
    this.startDate = '',
    this.endDate = '',
    this.description = '',
    this.achievements = const [],
    this.technologies = const [],
    this.skillsUsed = const [],
  });

  factory Experience.fromJson(
    Map<String, dynamic> json,
  ) {
    return Experience(
      company: _string(json['company']),
      role: _string(
        json['role'] ?? json['position'],
      ),
      startDate: _string(json['start_date']),
      endDate: _string(json['end_date']),
      description: _string(json['description']),
      achievements: _stringList(
        json['achievements'],
      ),
      technologies: _stringList(
        json['technologies'],
      ),
      skillsUsed: _stringList(
        json['skills_used'],
      ),
    );
  }
}

class Education {
  final String institution;
  final String degree;
  final String fieldOfStudy;
  final String educationLevel;
  final String location;
  final String startDate;
  final String endDate;
  final bool current;
  final String description;
  final String gpa;
  final List<String> honors;
  final double confidence;

  const Education({
    this.institution = '',
    this.degree = '',
    this.fieldOfStudy = '',
    this.educationLevel = '',
    this.location = '',
    this.startDate = '',
    this.endDate = '',
    this.current = false,
    this.description = '',
    this.gpa = '',
    this.honors = const [],
    this.confidence = 1.0,
  });

  factory Education.fromJson(
    Map<String, dynamic> json,
  ) {
    return Education(
      institution: _string(json['institution']),
      degree: _string(json['degree']),
      fieldOfStudy: _string(
        json['field_of_study'],
      ),
      educationLevel: _string(
        json['education_level'] ?? json['level'],
      ),
      location: _string(json['location']),
      startDate: _string(json['start_date']),
      endDate: _string(json['end_date']),
      current: _bool(json['current']),
      description: _string(json['description']),
      gpa: _string(json['gpa']),
      honors: _stringList(json['honors']),
      confidence: _double(
        json['confidence'],
        defaultValue: 1.0,
      ),
    );
  }
}

class ContinuousTraining {
  final String institution;
  final String degree;
  final String fieldOfStudy;
  final String educationLevel;
  final String location;
  final String startDate;
  final String endDate;
  final bool current;
  final String description;
  final String gpa;
  final List<String> honors;
  final double confidence;

  const ContinuousTraining({
    this.institution = '',
    this.degree = '',
    this.fieldOfStudy = '',
    this.educationLevel = '',
    this.location = '',
    this.startDate = '',
    this.endDate = '',
    this.current = false,
    this.description = '',
    this.gpa = '',
    this.honors = const [],
    this.confidence = 1.0,
  });

  factory ContinuousTraining.fromJson(
    Map<String, dynamic> json,
  ) {
    return ContinuousTraining(
      institution: _string(json['institution']),
      degree: _string(json['degree']),
      fieldOfStudy: _string(
        json['field_of_study'],
      ),
      educationLevel: _string(
        json['education_level'] ?? json['level'],
      ),
      location: _string(json['location']),
      startDate: _string(json['start_date']),
      endDate: _string(json['end_date']),
      current: _bool(json['current']),
      description: _string(json['description']),
      gpa: _string(json['gpa']),
      honors: _stringList(json['honors']),
      confidence: _double(
        json['confidence'],
        defaultValue: 1.0,
      ),
    );
  }
}

class Skill {
  final String name;
  final String category;
  final String level;
  final double? years;
  final double confidence;
  final String source;
  final bool verified;

  const Skill({
    this.name = '',
    this.category = '',
    this.level = '',
    this.years,
    this.confidence = 1.0,
    this.source = '',
    this.verified = false,
  });

  factory Skill.fromJson(
    Map<String, dynamic> json,
  ) {
    return Skill(
      name: _string(json['name']),
      category: _string(json['category']),
      level: _string(json['level']),
      years: _nullableDouble(json['years']),
      confidence: _double(
        json['confidence'],
        defaultValue: 1.0,
      ),
      source: _string(json['source']),
      verified: _bool(json['verified']),
    );
  }
}

class Skills {
  final List<Skill> items;

  const Skills({
    this.items = const [],
  });

  factory Skills.fromJson(
    dynamic json,
  ) {
    if (json is List) {
      return Skills(
        items: json
            .whereType<Map>()
            .map(
              (item) => Skill.fromJson(
                Map<String, dynamic>.from(item),
              ),
            )
            .toList(),
      );
    }

    if (json is Map<String, dynamic>) {
      final technical = _skillList(
        json['technical_skills'],
        'technical',
      );

      final soft = _skillList(
        json['soft_skills'],
        'soft',
      );

      final tools = _skillList(
        json['tools'],
        'technical',
      );

      final frameworks = _skillList(
        json['frameworks'],
        'technical',
      );

      final programming = _skillList(
        json['programming_languages'],
        'technical',
      );

      final databases = _skillList(
        json['databases'],
        'technical',
      );

      final cloud = _skillList(
        json['cloud'],
        'technical',
      );

      return Skills(
        items: [
          ...technical,
          ...soft,
          ...tools,
          ...frameworks,
          ...programming,
          ...databases,
          ...cloud,
        ],
      );
    }

    return const Skills();
  }

  List<Skill> get technicalSkills {
    return items
        .where(
          (skill) =>
              skill.category.toLowerCase() ==
              'technical',
        )
        .toList();
  }

  List<Skill> get softSkills {
    return items
        .where(
          (skill) =>
              skill.category.toLowerCase() ==
              'soft',
        )
        .toList();
  }
}

class Language {
  final String name;
  final String level;
  final bool native;
  final bool certified;
  final String? certification;
  final String? score;
  final double confidence;

  const Language({
    this.name = '',
    this.level = '',
    this.native = false,
    this.certified = false,
    this.certification,
    this.score,
    this.confidence = 1.0,
  });

  String get language => name;

  factory Language.fromJson(
    Map<String, dynamic> json,
  ) {
    return Language(
      name: _string(
        json['name'] ?? json['language'],
      ),
      level: _string(json['level']),
      native: _bool(json['native']),
      certified: _bool(json['certified']),
      certification:
          _nullableString(json['certification']),
      score: _nullableString(json['score']),
      confidence: _double(
        json['confidence'],
        defaultValue: 1.0,
      ),
    );
  }
}

class Certification {
  final String name;
  final String issuer;
  final String? credentialId;
  final String? credentialUrl;
  final String? issueDate;
  final String? expirationDate;
  final bool neverExpires;
  final List<String> skills;
  final bool verified;
  final double confidence;

  const Certification({
    this.name = '',
    this.issuer = '',
    this.credentialId,
    this.credentialUrl,
    this.issueDate,
    this.expirationDate,
    this.neverExpires = false,
    this.skills = const [],
    this.verified = false,
    this.confidence = 1.0,
  });

  String get provider => issuer;

  String get date => issueDate ?? '';

  factory Certification.fromJson(
    Map<String, dynamic> json,
  ) {
    return Certification(
      name: _string(json['name']),
      issuer: _string(
        json['issuer'] ?? json['provider'],
      ),
      credentialId:
          _nullableString(json['credential_id']),
      credentialUrl:
          _nullableString(json['credential_url']),
      issueDate:
          _nullableString(json['issue_date']),
      expirationDate:
          _nullableString(json['expiration_date']),
      neverExpires:
          _bool(json['never_expires']),
      skills: _stringList(json['skills']),
      verified: _bool(json['verified']),
      confidence: _double(
        json['confidence'],
        defaultValue: 1.0,
      ),
    );
  }
}

class Project {
  final String name;
  final String description;
  final String role;
  final String url;
  final List<String> technologies;
  final List<String> achievements;
  final double confidence;

  const Project({
    this.name = '',
    this.description = '',
    this.role = '',
    this.url = '',
    this.technologies = const [],
    this.achievements = const [],
    this.confidence = 1.0,
  });

  factory Project.fromJson(
    Map<String, dynamic> json,
  ) {
    return Project(
      name: _string(json['name']),
      description: _string(json['description']),
      role: _string(json['role']),
      url: _string(
        json['url'] ?? json['project_url'],
      ),
      technologies: _stringList(
        json['technologies'],
      ),
      achievements: _stringList(
        json['achievements'],
      ),
      confidence: _double(
        json['confidence'],
        defaultValue: 1.0,
      ),
    );
  }
}

class ATSMetrics {
  final int atsScore;
  final List<String> detectedKeywords;
  final List<String> missingKeywords;
  final String compatibility;
  final List<String> observations;

  const ATSMetrics({
    this.atsScore = 0,
    this.detectedKeywords = const [],
    this.missingKeywords = const [],
    this.compatibility = '',
    this.observations = const [],
  });

  factory ATSMetrics.fromJson(
    dynamic json,
  ) {
    if (json is! Map) {
      return const ATSMetrics();
    }

    return ATSMetrics(
      atsScore: _int(json['ats_score']),
      detectedKeywords:
          _stringList(json['detected_keywords']),
      missingKeywords:
          _stringList(json['missing_keywords']),
      compatibility:
          _string(json['compatibility']),
      observations:
          _stringList(json['observations']),
    );
  }
}

class LinkedInMetrics {
  final int score;
  final String profileLevel;
  final List<String> observations;
  final List<String> recommendations;

  const LinkedInMetrics({
    this.score = 0,
    this.profileLevel = '',
    this.observations = const [],
    this.recommendations = const [],
  });

  factory LinkedInMetrics.fromJson(
    dynamic json,
  ) {
    if (json is! Map) {
      return const LinkedInMetrics();
    }

    return LinkedInMetrics(
      score: _int(json['score']),
      profileLevel:
          _string(json['profile_level']),
      observations:
          _stringList(json['observations']),
      recommendations:
          _stringList(json['recommendations']),
    );
  }
}

class CareerMetrics {
  final List<String> strengths;
  final List<String> weaknesses;
  final List<String> areasForImprovement;
  final String employabilityLevel;

  const CareerMetrics({
    this.strengths = const [],
    this.weaknesses = const [],
    this.areasForImprovement = const [],
    this.employabilityLevel = '',
  });

  factory CareerMetrics.fromJson(
    dynamic json,
  ) {
    if (json is! Map) {
      return const CareerMetrics();
    }

    return CareerMetrics(
      strengths: _stringList(json['strengths']),
      weaknesses: _stringList(json['weaknesses']),
      areasForImprovement:
          _stringList(json['areas_for_improvement']),
      employabilityLevel:
          _string(json['employability_level']),
    );
  }
}

class ProfessionalProfile {
  final String id;
  final String userId;
  final PersonalInfo personalInfo;

  final List<Experience> experience;
  final List<Education> education;
  final List<ContinuousTraining> continuousTraining;
  final Skills skills;
  final List<Language> languages;
  final List<Certification> certifications;
  final List<Project> projects;

  final ATSMetrics atsMetrics;
  final LinkedInMetrics linkedinMetrics;
  final CareerMetrics careerMetrics;

  final List<String> cvKeywords;
  final int cvScore;

  const ProfessionalProfile({
    required this.id,
    this.userId = '',
    required this.personalInfo,
    this.experience = const [],
    this.education = const [],
    this.continuousTraining = const [],
    required this.skills,
    this.languages = const [],
    this.certifications = const [],
    this.projects = const [],
    required this.atsMetrics,
    required this.linkedinMetrics,
    required this.careerMetrics,
    this.cvKeywords = const [],
    this.cvScore = 0,
  });

  factory ProfessionalProfile.fromJson(
    Map<String, dynamic> json,
  ) {
    return ProfessionalProfile(
      id: _string(json['id']),
      userId: _string(json['user_id']),
      personalInfo: PersonalInfo.fromJson(
        _map(json['personal_info']),
      ),
      experience: _objectList(
        json['experience'],
        Experience.fromJson,
      ),
      education: _objectList(
        json['education'],
        Education.fromJson,
      ),
      continuousTraining: _objectList(
        json['continuous_training'],
        ContinuousTraining.fromJson,
      ),
      skills: Skills.fromJson(
        json['skills'],
      ),
      languages: _objectList(
        json['languages'],
        Language.fromJson,
      ),
      certifications: _objectList(
        json['certifications'],
        Certification.fromJson,
      ),
      projects: _objectList(
        json['projects'],
        Project.fromJson,
      ),
      atsMetrics: ATSMetrics.fromJson(
        json['ats_metrics'],
      ),
      linkedinMetrics: LinkedInMetrics.fromJson(
        json['linkedin_metrics'],
      ),
      careerMetrics: CareerMetrics.fromJson(
        json['career_metrics'],
      ),
      cvKeywords: _stringList(
        json['cv_keywords'],
      ),
      cvScore: _int(json['cv_score']),
    );
  }
}

/* -------------------------------------------------------------------------- */
/* Helpers                                                                    */
/* -------------------------------------------------------------------------- */

String _string(dynamic value) {
  if (value == null) {
    return '';
  }

  return value.toString();
}

String? _nullableString(dynamic value) {
  if (value == null) {
    return null;
  }

  return value.toString();
}

int _int(
  dynamic value, {
  int defaultValue = 0,
}) {
  if (value is int) {
    return value;
  }

  if (value is num) {
    return value.toInt();
  }

  if (value is String) {
    return int.tryParse(value) ?? defaultValue;
  }

  return defaultValue;
}

double _double(
  dynamic value, {
  double defaultValue = 0.0,
}) {
  if (value is double) {
    return value;
  }

  if (value is num) {
    return value.toDouble();
  }

  if (value is String) {
    return double.tryParse(value) ?? defaultValue;
  }

  return defaultValue;
}

double? _nullableDouble(dynamic value) {
  if (value == null) {
    return null;
  }

  if (value is num) {
    return value.toDouble();
  }

  if (value is String) {
    return double.tryParse(value);
  }

  return null;
}

bool _bool(dynamic value) {
  if (value is bool) {
    return value;
  }

  if (value is String) {
    return value.toLowerCase() == 'true';
  }

  if (value is num) {
    return value != 0;
  }

  return false;
}

Map<String, dynamic> _map(dynamic value) {
  if (value is Map<String, dynamic>) {
    return value;
  }

  if (value is Map) {
    return Map<String, dynamic>.from(value);
  }

  return <String, dynamic>{};
}

List<String> _stringList(dynamic value) {
  if (value is! List) {
    return const [];
  }

  return value.map((item) => item.toString()).toList();
}

List<Skill> _skillList(dynamic value, [String? category]) {
  if (value is! List) {
    return const [];
  }

  final List<Skill> result = [];
  for (final item in value) {
    if (item is Map) {
      result.add(Skill.fromJson(Map<String, dynamic>.from(item)));
    } else if (item is String) {
      result.add(Skill(name: item, category: category ?? 'technical'));
    }
  }
  return result;
}

List<T> _objectList<T>(
  dynamic value,
  T Function(Map<String, dynamic>) factory,
) {
  if (value is! List) {
    return const [];
  }

  return value
      .whereType<Map>()
      .map(
        (item) => factory(
          Map<String, dynamic>.from(item),
        ),
      )
      .toList();
}