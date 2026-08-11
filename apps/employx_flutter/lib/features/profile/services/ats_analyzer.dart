import '../../../core/models/professional_profile_model.dart';

class ATSBreakdown {
  final int keywordMatch;
  final int roleMatch;
  final int skillsCoverage;
  final int experienceMatch;
  final int educationMatch;

  const ATSBreakdown({
    required this.keywordMatch,
    required this.roleMatch,
    required this.skillsCoverage,
    required this.experienceMatch,
    required this.educationMatch,
  });
}

class ATSAnalysisResult {
  final int score;
  final ATSBreakdown breakdown;
  final List<String> matchedKeywords;
  final List<String> missingKeywords;
  final List<String> recommendations;

  const ATSAnalysisResult({
    required this.score,
    required this.breakdown,
    required this.matchedKeywords,
    required this.missingKeywords,
    required this.recommendations,
  });
}

/// Deterministic, explainable ATS-style matcher.
///
/// This is intentionally a job-specific match score, not a claim about how
/// any particular employer ATS scores candidates. The job description is the
/// source of truth for the comparison.
class ATSAnalyzer {
  const ATSAnalyzer();

  ATSAnalysisResult analyze(
    ProfessionalProfile profile,
    String jobDescription,
  ) {
    final jobText = _normalize(jobDescription);

    if (jobText.trim().isEmpty) {
      return const ATSAnalysisResult(
        score: 0,
        breakdown: ATSBreakdown(
          keywordMatch: 0,
          roleMatch: 0,
          skillsCoverage: 0,
          experienceMatch: 0,
          educationMatch: 0,
        ),
        matchedKeywords: [],
        missingKeywords: [],
        recommendations: [
          'Pega una descripción de vacante para calcular el ATS Match.',
        ],
      );
    }

    final profileCorpus = _normalize(_profileCorpus(profile));
    final profileTerms = _profileTerms(profile);
    final jobKeywords = _extractJobKeywords(jobText);

    final matched = <String>[];
    final missing = <String>[];

    for (final keyword in jobKeywords) {
      if (_containsTerm(profileCorpus, keyword)) {
        matched.add(keyword);
      } else {
        missing.add(keyword);
      }
    }

    final keywordRatio = jobKeywords.isEmpty
        ? 0.0
        : matched.length / jobKeywords.length;

    final skillHits = profileTerms.skills
        .where((skill) => _containsTerm(jobText, _normalize(skill)))
        .length;
    final skillTotal = profileTerms.skills.length;
    final skillsRatio = skillTotal == 0 ? 0.0 : skillHits / skillTotal;

    final roleMatch = _roleScore(profile, jobText);
    final experienceMatch = _experienceScore(profile, jobText);
    final educationMatch = _educationScore(profile, jobText);

    final score = _clampInt(
      (keywordRatio * 50) +
          (roleMatch * 0.20) +
          (skillsRatio * 15) +
          (experienceMatch * 10) +
          (educationMatch * 5),
    );

    final recommendations = <String>[];

    if (keywordRatio < 0.70) {
      recommendations.add(
        'Alinea el CV con las palabras clave de la vacante que realmente describan tu experiencia.',
      );
    }
    if (roleMatch < 60) {
      recommendations.add(
        'Revisa el título profesional y el resumen para reflejar el rol objetivo cuando sea verídico.',
      );
    }
    if (skillsRatio < 0.60) {
      recommendations.add(
        'Haz más visibles las habilidades técnicas relevantes que ya dominas.',
      );
    }
    if (experienceMatch < 60) {
      recommendations.add(
        'Refuerza la experiencia con logros, responsabilidades y tecnologías relacionadas con la vacante.',
      );
    }
    if (educationMatch < 60) {
      recommendations.add(
        'Verifica que la formación o certificaciones relevantes estén claramente expresadas.',
      );
    }
    if (recommendations.isEmpty) {
      recommendations.add(
        'Buen nivel de alineación. Revisa los términos faltantes antes de aplicar.',
      );
    }

    return ATSAnalysisResult(
      score: score,
      breakdown: ATSBreakdown(
        keywordMatch: (keywordRatio * 100).round(),
        roleMatch: roleMatch,
        skillsCoverage: (skillsRatio * 100).round(),
        experienceMatch: experienceMatch,
        educationMatch: educationMatch,
      ),
      matchedKeywords: matched.take(20).toList(),
      missingKeywords: missing.take(20).toList(),
      recommendations: recommendations.take(5).toList(),
    );
  }

  String _profileCorpus(ProfessionalProfile profile) {
    final values = <String>[
      profile.personalInfo.name,
      profile.personalInfo.professionalSummary,
      profile.personalInfo.currentPosition,
      profile.personalInfo.careerGoal,
      ...profile.cvKeywords,
      ...profile.skills.items.map((s) => s.name),
      ...profile.experience.expand(
        (e) => [
          e.role,
          e.company,
          e.description,
          ...e.achievements,
          ...e.technologies,
          ...e.skillsUsed,
        ],
      ),
      ...profile.education.expand(
        (e) => [e.degree, e.fieldOfStudy, e.educationLevel, e.description],
      ),
      ...profile.certifications.expand((c) => [c.name, c.issuer, ...c.skills]),
      ...profile.projects.expand(
        (p) => [p.name, p.description, p.role, ...p.technologies, ...p.achievements],
      ),
      ...profile.languages.map((l) => '${l.name} ${l.level}'),
    ];

    return values.where((v) => v.trim().isNotEmpty).join(' ');
  }

  _ProfileTerms _profileTerms(ProfessionalProfile profile) {
    return _ProfileTerms(
      skills: profile.skills.items
          .map((s) => s.name.trim())
          .where((s) => s.isNotEmpty)
          .toSet()
          .toList(),
    );
  }

  List<String> _extractJobKeywords(String text) {
    final tokens = text
        .split(RegExp(r'[^a-z0-9+#./-]+'))
        .map(_normalize)
        .where((token) => token.length >= 3)
        .where((token) => !_stopWords.contains(token))
        .toSet()
        .toList();

    tokens.sort((a, b) => b.length.compareTo(a.length));
    return tokens.take(40).toList();
  }

  int _roleScore(ProfessionalProfile profile, String jobText) {
    final role = _normalize(profile.personalInfo.currentPosition);
    if (role.isEmpty) return 35;
    if (_containsTerm(jobText, role)) return 100;

    final roleTokens = role
        .split(RegExp(r'\s+'))
        .where((t) => t.length >= 3 && !_stopWords.contains(t));
    final total = roleTokens.length;
    if (total == 0) return 35;

    final hits = roleTokens.where((t) => jobText.contains(t)).length;
    return ((hits / total) * 100).round().clamp(0, 100);
  }

  int _experienceScore(ProfessionalProfile profile, String jobText) {
    if (profile.experience.isEmpty) return 25;

    final relevant = profile.experience.where((experience) {
      final text = _normalize(
        '${experience.role} ${experience.description} ${experience.technologies.join(' ')}',
      );
      return text.split(RegExp(r'\s+')).any(
        (token) => token.length >= 4 && jobText.contains(token),
      );
    }).length;

    return ((relevant / profile.experience.length) * 100).round().clamp(0, 100);
  }

  int _educationScore(ProfessionalProfile profile, String jobText) {
    final educationText = _normalize([
      ...profile.education.expand((e) => [e.degree, e.fieldOfStudy, e.educationLevel]),
      ...profile.certifications.expand((c) => [c.name, c.issuer, ...c.skills]),
    ].join(' '));

    if (educationText.isEmpty) return 25;
    if (jobText.contains(educationText)) return 100;

    final tokens = educationText
        .split(RegExp(r'\s+'))
        .where((t) => t.length >= 4 && !_stopWords.contains(t))
        .toSet();
    if (tokens.isEmpty) return 25;

    final hits = tokens.where(jobText.contains).length;
    return ((hits / tokens.length) * 100).round().clamp(0, 100);
  }

  bool _containsTerm(String corpus, String term) {
    if (term.isEmpty) return false;
    if (term.contains(' ') || term.contains('/') || term.contains('+')) {
      return corpus.contains(term);
    }
    return RegExp(r'(^|[^a-z0-9+#])' + RegExp.escape(term) + r'([^a-z0-9+#]|$)')
        .hasMatch(corpus);
  }

  String _normalize(String value) {
    return value
        .toLowerCase()
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u')
        .replaceAll('ü', 'u')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
  }

  int _clampInt(double value) => value.round().clamp(0, 100);

  static const Set<String> _stopWords = {
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'are', 'you', 'your',
    'our', 'their', 'have', 'has', 'will', 'can', 'not', 'but', 'all', 'any',
    'una', 'uno', 'unos', 'unas', 'los', 'las', 'del', 'para', 'con', 'por',
    'que', 'como', 'sus', 'esta', 'este', 'estas', 'estos', 'ser', 'sea',
  };
}

class _ProfileTerms {
  final List<String> skills;

  const _ProfileTerms({required this.skills});
}
