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

  PersonalInfo({
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
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      location: json['location'] ?? '',
      linkedin: json['linkedin'] ?? '',
      portfolio: json['portfolio'] ?? '',
      website: json['website'] ?? '',
      professionalSummary: json['professional_summary'] ?? '',
      careerGoal: json['career_goal'] ?? '',
      currentPosition: json['current_position'] ?? '',
      yearsOfExperience: json['years_of_experience'] ?? 0,
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

  Experience({
    this.company = '',
    this.role = '',
    this.startDate = '',
    this.endDate = '',
    this.description = '',
    this.achievements = const [],
    this.technologies = const [],
    this.skillsUsed = const [],
  });

  factory Experience.fromJson(Map<String, dynamic> json) {
    return Experience(
      company: json['company'] ?? '',
      role: json['role'] ?? '',
      startDate: json['start_date'] ?? '',
      endDate: json['end_date'] ?? '',
      description: json['description'] ?? '',
      achievements: List<String>.from(json['achievements'] ?? []),
      technologies: List<String>.from(json['technologies'] ?? []),
      skillsUsed: List<String>.from(json['skills_used'] ?? []),
    );
  }
}

class Education {
  final String institution;
  final String degree;
  final String level;
  final String period;

  Education({
    this.institution = '',
    this.degree = '',
    this.level = '',
    this.period = '',
  });

  factory Education.fromJson(Map<String, dynamic> json) {
    return Education(
      institution: json['institution'] ?? '',
      degree: json['degree'] ?? '',
      level: json['level'] ?? '',
      period: json['period'] ?? '',
    );
  }
}

class Skills {
  final List<String> technicalSkills;
  final List<String> softSkills;
  final List<String> tools;
  final List<String> frameworks;
  final List<String> programmingLanguages;
  final List<String> databases;
  final List<String> cloud;

  Skills({
    this.technicalSkills = const [],
    this.softSkills = const [],
    this.tools = const [],
    this.frameworks = const [],
    this.programmingLanguages = const [],
    this.databases = const [],
    this.cloud = const [],
  });

  factory Skills.fromJson(Map<String, dynamic> json) {
    return Skills(
      technicalSkills: List<String>.from(json['technical_skills'] ?? []),
      softSkills: List<String>.from(json['soft_skills'] ?? []),
      tools: List<String>.from(json['tools'] ?? []),
      frameworks: List<String>.from(json['frameworks'] ?? []),
      programmingLanguages: List<String>.from(json['programming_languages'] ?? []),
      databases: List<String>.from(json['databases'] ?? []),
      cloud: List<String>.from(json['cloud'] ?? []),
    );
  }
}

class Language {
  final String language;
  final String level;
  final String certification;

  Language({
    this.language = '',
    this.level = '',
    this.certification = '',
  });

  factory Language.fromJson(Map<String, dynamic> json) {
    return Language(
      language: json['language'] ?? '',
      level: json['level'] ?? '',
      certification: json['certification'] ?? '',
    );
  }
}

class Certification {
  final String name;
  final String provider;
  final String date;

  Certification({
    this.name = '',
    this.provider = '',
    this.date = '',
  });

  factory Certification.fromJson(Map<String, dynamic> json) {
    return Certification(
      name: json['name'] ?? '',
      provider: json['provider'] ?? '',
      date: json['date'] ?? '',
    );
  }
}

class ATSMetrics {
  final int atsScore;
  final List<String> detectedKeywords;
  final List<String> missingKeywords;
  final String compatibility;
  final List<String> observations;

  ATSMetrics({
    this.atsScore = 0,
    this.detectedKeywords = const [],
    this.missingKeywords = const [],
    this.compatibility = '',
    this.observations = const [],
  });

  factory ATSMetrics.fromJson(Map<String, dynamic> json) {
    return ATSMetrics(
      atsScore: json['ats_score'] ?? 0,
      detectedKeywords: List<String>.from(json['detected_keywords'] ?? []),
      missingKeywords: List<String>.from(json['missing_keywords'] ?? []),
      compatibility: json['compatibility'] ?? '',
      observations: List<String>.from(json['observations'] ?? []),
    );
  }
}

class LinkedInMetrics {
  final int score;
  final String profileLevel;
  final List<String> observations;
  final List<String> recommendations;

  LinkedInMetrics({
    this.score = 0,
    this.profileLevel = '',
    this.observations = const [],
    this.recommendations = const [],
  });

  factory LinkedInMetrics.fromJson(Map<String, dynamic> json) {
    return LinkedInMetrics(
      score: json['score'] ?? 0,
      profileLevel: json['profile_level'] ?? '',
      observations: List<String>.from(json['observations'] ?? []),
      recommendations: List<String>.from(json['recommendations'] ?? []),
    );
  }
}

class CareerMetrics {
  final List<String> strengths;
  final List<String> weaknesses;
  final List<String> areasForImprovement;
  final String employabilityLevel;

  CareerMetrics({
    this.strengths = const [],
    this.weaknesses = const [],
    this.areasForImprovement = const [],
    this.employabilityLevel = '',
  });

  factory CareerMetrics.fromJson(Map<String, dynamic> json) {
    return CareerMetrics(
      strengths: List<String>.from(json['strengths'] ?? []),
      weaknesses: List<String>.from(json['weaknesses'] ?? []),
      areasForImprovement: List<String>.from(json['areas_for_improvement'] ?? []),
      employabilityLevel: json['employability_level'] ?? '',
    );
  }
}

class ProfessionalProfile {
  final String id;
  final String userId;
  final PersonalInfo personalInfo;
  final List<Experience> experience;
  final List<Education> education;
  final Skills skills;
  final List<Language> languages;
  final List<Certification> certifications;
  final ATSMetrics atsMetrics;
  final LinkedInMetrics linkedinMetrics;
  final CareerMetrics careerMetrics;
  final List<String> cvKeywords;
  final int cvScore;

  ProfessionalProfile({
    required this.id,
    this.userId = '',
    required this.personalInfo,
    this.experience = const [],
    this.education = const [],
    required this.skills,
    this.languages = const [],
    this.certifications = const [],
    required this.atsMetrics,
    required this.linkedinMetrics,
    required this.careerMetrics,
    this.cvKeywords = const [],
    this.cvScore = 0,
  });

  factory ProfessionalProfile.fromJson(Map<String, dynamic> json) {
    return ProfessionalProfile(
      id: json['id'] ?? '',
      userId: json['user_id'] ?? '',
      personalInfo: PersonalInfo.fromJson(json['personal_info'] ?? {}),
      experience: (json['experience'] as List?)?.map((e) => Experience.fromJson(e)).toList() ?? [],
      education: (json['education'] as List?)?.map((e) => Education.fromJson(e)).toList() ?? [],
      skills: Skills.fromJson(json['skills'] ?? {}),
      languages: (json['languages'] as List?)?.map((e) => Language.fromJson(e)).toList() ?? [],
      certifications: (json['certifications'] as List?)?.map((e) => Certification.fromJson(e)).toList() ?? [],
      atsMetrics: ATSMetrics.fromJson(json['ats_metrics'] ?? {}),
      linkedinMetrics: LinkedInMetrics.fromJson(json['linkedin_metrics'] ?? {}),
      careerMetrics: CareerMetrics.fromJson(json['career_metrics'] ?? {}),
      cvKeywords: List<String>.from(json['cv_keywords'] ?? []),
      cvScore: json['cv_score'] ?? 0,
    );
  }
}
