import '../../../core/models/professional_profile_model.dart';

/// Resultado detallado del análisis ATS.
///
/// Representa la compatibilidad entre un perfil profesional
/// y una vacante específica.
class ATSAnalysisResult {
  final int score;

  final int keywordMatch;
  final int roleMatch;
  final int skillsMatch;
  final int experienceMatch;
  final int educationMatch;

  final List<String> matchedKeywords;
  final List<String> missingKeywords;
  final List<String> recommendations;

  const ATSAnalysisResult({
    required this.score,
    required this.keywordMatch,
    required this.roleMatch,
    required this.skillsMatch,
    required this.experienceMatch,
    required this.educationMatch,
    required this.matchedKeywords,
    required this.missingKeywords,
    required this.recommendations,
  });

  bool get hasAnalysis => score > 0;

  String get compatibility {
    if (score >= 85) {
      return 'Excelente';
    }

    if (score >= 70) {
      return 'Alta';
    }

    if (score >= 55) {
      return 'Moderada';
    }

    if (score >= 40) {
      return 'Baja';
    }

    return 'Muy baja';
  }
}

/// Motor ATS de LIA-EmployX.
///
/// Compara el perfil profesional contra la descripción
/// de una vacante y genera un resultado explicable.
class ATSAnalyzer {
  const ATSAnalyzer();

  ATSAnalysisResult analyze({
    required ProfessionalProfile profile,
    required String jobDescription,
  }) {
    final normalizedJob = _normalize(jobDescription);

    if (normalizedJob.isEmpty) {
      return const ATSAnalysisResult(
        score: 0,
        keywordMatch: 0,
        roleMatch: 0,
        skillsMatch: 0,
        experienceMatch: 0,
        educationMatch: 0,
        matchedKeywords: [],
        missingKeywords: [],
        recommendations: [
          'Agrega una descripción de la vacante para iniciar el análisis ATS.',
        ],
      );
    }

    final profileText = _buildProfileText(profile);
    final jobKeywords = _extractKeywords(normalizedJob);

    final matchedKeywords = <String>[];
    final missingKeywords = <String>[];

    for (final keyword in jobKeywords) {
      if (_containsTerm(profileText, keyword)) {
        matchedKeywords.add(keyword);
      } else {
        missingKeywords.add(keyword);
      }
    }

    final keywordMatch = _percentage(
      matchedKeywords.length,
      jobKeywords.length,
    );

    final skillsMatch = _calculateSkillsMatch(
      profile,
      normalizedJob,
    );

    final roleMatch = _calculateRoleMatch(
      profile,
      normalizedJob,
    );

    final experienceMatch = _calculateExperienceMatch(
      profile,
      normalizedJob,
    );

    final educationMatch = _calculateEducationMatch(
      profile,
      normalizedJob,
    );

    final score = _clampScore(
      (keywordMatch * 0.40) +
          (skillsMatch * 0.25) +
          (roleMatch * 0.15) +
          (experienceMatch * 0.15) +
          (educationMatch * 0.05),
    );

    final recommendations = _buildRecommendations(
      keywordMatch: keywordMatch,
      roleMatch: roleMatch,
      skillsMatch: skillsMatch,
      experienceMatch: experienceMatch,
      educationMatch: educationMatch,
      missingKeywords: missingKeywords,
    );

    return ATSAnalysisResult(
      score: score,
      keywordMatch: keywordMatch,
      roleMatch: roleMatch,
      skillsMatch: skillsMatch,
      experienceMatch: experienceMatch,
      educationMatch: educationMatch,
      matchedKeywords: matchedKeywords,
      missingKeywords: missingKeywords,
      recommendations: recommendations,
    );
  }

  // ---------------------------------------------------------------------------
  // PROFILE CORPUS
  // ---------------------------------------------------------------------------

  String _buildProfileText(
    ProfessionalProfile profile,
  ) {
    final values = <String>[
      profile.personalInfo.name,
      profile.personalInfo.professionalSummary,
      profile.personalInfo.careerGoal,
      profile.personalInfo.currentPosition,

      ...profile.cvKeywords,

      // Skills
      ...profile.skills.items.map(
        (skill) => [
          skill.name,
          skill.category,
          skill.level,
        ].join(' '),
      ),

      // Experience
      ...profile.experience.expand(
        (experience) => [
          experience.company,
          experience.role,
          experience.description,
          ...experience.achievements,
          ...experience.technologies,
          ...experience.skillsUsed,
        ],
      ),

      // Education
      ...profile.education.expand(
        (education) => [
          education.institution,
          education.degree,
          education.fieldOfStudy,
          education.educationLevel,
          education.description,
          ...education.honors,
        ],
      ),

      // Continuous training
      ...profile.continuousTraining.expand(
        (training) => [
          training.institution,
          training.degree,
          training.fieldOfStudy,
          training.educationLevel,
          training.description,
          ...training.honors,
        ],
      ),

      // Certifications
      ...profile.certifications.expand(
        (certification) => [
          certification.name,
          certification.issuer,
          ...certification.skills,
        ],
      ),

      // Projects
      ...profile.projects.expand(
        (project) => [
          project.name,
          project.description,
          project.role,
          ...project.technologies,
          ...project.achievements,
        ],
      ),

      // Languages
      ...profile.languages.expand(
        (language) => [
          language.name,
          language.level,
          language.certification ?? '',
        ],
      ),
    ];

    return _normalize(
      values
          .where(
            (value) => value.trim().isNotEmpty,
          )
          .join(' '),
    );
  }

  // ---------------------------------------------------------------------------
  // KEYWORDS
  // ---------------------------------------------------------------------------

  List<String> _extractKeywords(
    String text,
  ) {
    final words = text
        .split(
          RegExp(
            r'[^a-z0-9+#./-]+',
          ),
        )
        .map(_normalize)
        .where(
          (word) => word.length >= 3,
        )
        .where(
          (word) => !_stopWords.contains(word),
        )
        .toSet()
        .toList();

    words.sort(
      (a, b) => b.length.compareTo(
        a.length,
      ),
    );

    return words.take(40).toList();
  }

  // ---------------------------------------------------------------------------
  // SKILLS
  // ---------------------------------------------------------------------------

  int _calculateSkillsMatch(
    ProfessionalProfile profile,
    String jobText,
  ) {
    final skills = profile.skills.items
        .map(
          (skill) => _normalize(skill.name),
        )
        .where(
          (skill) => skill.isNotEmpty,
        )
        .toSet()
        .toList();

    if (skills.isEmpty) {
      return 0;
    }

    final matched = skills.where(
      (skill) => _containsTerm(
        jobText,
        skill,
      ),
    );

    return _percentage(
      matched.length,
      skills.length,
    );
  }

  // ---------------------------------------------------------------------------
  // ROLE
  // ---------------------------------------------------------------------------

  int _calculateRoleMatch(
    ProfessionalProfile profile,
    String jobText,
  ) {
    final currentPosition = _normalize(
      profile.personalInfo.currentPosition,
    );

    final careerGoal = _normalize(
      profile.personalInfo.careerGoal,
    );

    final roles = <String>[
      currentPosition,
      careerGoal,
      ...profile.experience.map(
        (experience) => _normalize(
          experience.role,
        ),
      ),
      ...profile.projects.map(
        (project) => _normalize(
          project.role,
        ),
      ),
    ].where(
      (role) => role.isNotEmpty,
    );

    if (roles.isEmpty) {
      return 0;
    }

    int bestScore = 0;

    for (final role in roles) {
      if (_containsTerm(jobText, role)) {
        bestScore = 100;
        continue;
      }

      final tokens = role
          .split(RegExp(r'\s+'))
          .where(
            (token) =>
                token.length >= 3 &&
                !_stopWords.contains(token),
          )
          .toSet();

      if (tokens.isEmpty) {
        continue;
      }

      final matches = tokens.where(
        (token) => jobText.contains(token),
      );

      final partial = _percentage(
        matches.length,
        tokens.length,
      );

      if (partial > bestScore) {
        bestScore = partial;
      }
    }

    return bestScore;
  }

  // ---------------------------------------------------------------------------
  // EXPERIENCE
  // ---------------------------------------------------------------------------

  int _calculateExperienceMatch(
    ProfessionalProfile profile,
    String jobText,
  ) {
    if (profile.experience.isEmpty) {
      return 0;
    }

    int relevantExperiences = 0;

    for (final experience in profile.experience) {
      final experienceText = _normalize(
        [
          experience.role,
          experience.description,
          ...experience.technologies,
          ...experience.skillsUsed,
          ...experience.achievements,
        ].join(' '),
      );

      final tokens = experienceText
          .split(RegExp(r'\s+'))
          .where(
            (token) =>
                token.length >= 4 &&
                !_stopWords.contains(token),
          )
          .toSet();

      final hasRelevantTerm = tokens.any(
        (token) => jobText.contains(token),
      );

      if (hasRelevantTerm) {
        relevantExperiences++;
      }
    }

    return _percentage(
      relevantExperiences,
      profile.experience.length,
    );
  }

  // ---------------------------------------------------------------------------
  // EDUCATION
  // ---------------------------------------------------------------------------

  int _calculateEducationMatch(
    ProfessionalProfile profile,
    String jobText,
  ) {
    final educationValues = <String>[
      ...profile.education.expand(
        (education) => [
          education.degree,
          education.fieldOfStudy,
          education.educationLevel,
        ],
      ),
      ...profile.continuousTraining.expand(
        (training) => [
          training.degree,
          training.fieldOfStudy,
          training.educationLevel,
        ],
      ),
      ...profile.certifications.expand(
        (certification) => [
          certification.name,
          certification.issuer,
          ...certification.skills,
        ],
      ),
    ];

    final values = educationValues
        .map(_normalize)
        .where(
          (value) => value.isNotEmpty,
        )
        .toSet();

    if (values.isEmpty) {
      return 0;
    }

    final matched = values.where(
      (value) => _containsTerm(
        jobText,
        value,
      ),
    );

    return _percentage(
      matched.length,
      values.length,
    );
  }

  // ---------------------------------------------------------------------------
  // RECOMMENDATIONS
  // ---------------------------------------------------------------------------

  List<String> _buildRecommendations({
    required int keywordMatch,
    required int roleMatch,
    required int skillsMatch,
    required int experienceMatch,
    required int educationMatch,
    required List<String> missingKeywords,
  }) {
    final recommendations = <String>[];

    if (keywordMatch < 70) {
      recommendations.add(
        'Aumenta la coincidencia de palabras clave relevantes con la vacante.',
      );
    }

    if (skillsMatch < 70) {
      recommendations.add(
        'Haz más visibles las habilidades técnicas relacionadas con el puesto.',
      );
    }

    if (roleMatch < 70) {
      recommendations.add(
        'Revisa el título profesional y el objetivo para alinearlos con el rol objetivo cuando sea verídico.',
      );
    }

    if (experienceMatch < 70) {
      recommendations.add(
        'Destaca experiencias, tecnologías y logros directamente relacionados con la vacante.',
      );
    }

    if (educationMatch < 60) {
      recommendations.add(
        'Verifica que la formación, certificaciones y especializaciones relevantes estén claramente visibles.',
      );
    }

    if (missingKeywords.isNotEmpty) {
      final visibleMissing = missingKeywords.take(5).join(', ');

      recommendations.add(
        'Revisa estos términos de la vacante: $visibleMissing.',
      );
    }

    if (recommendations.isEmpty) {
      recommendations.add(
        'El perfil presenta una buena alineación con la vacante. Revisa los términos faltantes antes de aplicar.',
      );
    }

    return recommendations.take(6).toList();
  }

  // ---------------------------------------------------------------------------
  // NORMALIZATION
  // ---------------------------------------------------------------------------

  String _normalize(
    String value,
  ) {
    return value
        .toLowerCase()
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u')
        .replaceAll('ü', 'u')
        .replaceAll(
          RegExp(r'\s+'),
          ' ',
        )
        .trim();
  }

  bool _containsTerm(
    String corpus,
    String term,
  ) {
    if (term.isEmpty) {
      return false;
    }

    if (term.contains(' ') ||
        term.contains('/') ||
        term.contains('+') ||
        term.contains('.') ||
        term.contains('#')) {
      return corpus.contains(term);
    }

    return RegExp(
      r'(^|[^a-z0-9])' +
          RegExp.escape(term) +
          r'([^a-z0-9]|$)',
    ).hasMatch(corpus);
  }

  // ---------------------------------------------------------------------------
  // HELPERS
  // ---------------------------------------------------------------------------

  int _percentage(
    int matched,
    int total,
  ) {
    if (total <= 0) {
      return 0;
    }

    return ((matched / total) * 100)
        .round()
        .clamp(0, 100);
  }

  int _clampScore(
    double value,
  ) {
    return value
        .round()
        .clamp(0, 100);
  }

  // ---------------------------------------------------------------------------
  // STOP WORDS
  // ---------------------------------------------------------------------------

  static const Set<String> _stopWords = {
    // English
    'the',
    'and',
    'for',
    'with',
    'from',
    'that',
    'this',
    'these',
    'those',
    'are',
    'you',
    'your',
    'our',
    'their',
    'have',
    'has',
    'will',
    'can',
    'not',
    'but',
    'all',
    'any',
    'into',
    'about',
    'using',
    'use',
    'work',
    'working',
    'years',

    // Spanish
    'una',
    'uno',
    'unos',
    'unas',
    'los',
    'las',
    'del',
    'para',
    'con',
    'por',
    'que',
    'como',
    'sus',
    'esta',
    'este',
    'estas',
    'estos',
    'ser',
    'sea',
    'son',
    'más',
    'entre',
    'sobre',
    'desde',
    'tiene',
    'tener',
    'años',
  };
}