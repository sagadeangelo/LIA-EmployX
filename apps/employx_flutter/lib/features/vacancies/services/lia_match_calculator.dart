import 'dart:math';

import '../../../core/models/professional_profile_model.dart';
import '../models/vacancy_model.dart';

/// Desglose explicable de compatibilidad Match LIA.
class LiaMatchBreakdown {
  final int overall;
  final int skillsScore;
  final int experienceScore;
  final int titleScore;
  final int modalityScore;
  final int locationScore;

  const LiaMatchBreakdown({
    required this.overall,
    required this.skillsScore,
    required this.experienceScore,
    required this.titleScore,
    required this.modalityScore,
    required this.locationScore,
  });

  @override
  String toString() =>
      'LiaMatchBreakdown(overall: $overall%, skills: $skillsScore%, exp: $experienceScore%, title: $titleScore%, mod: $modalityScore%, loc: $locationScore%)';
}

/// Calculador determinista y explicable de Match LIA entre un candidato y una vacante.
class LiaMatchCalculator {
  const LiaMatchCalculator._();

  static const double weightSkills = 0.35;
  static const double weightExperience = 0.25;
  static const double weightTitle = 0.20;
  static const double weightModality = 0.10;
  static const double weightLocation = 0.10;

  /// Calcula el Match LIA entre una vacante y el perfil del usuario.
  static LiaMatchBreakdown calculate({
    required VacancyModel vacancy,
    required ProfessionalProfile? profile,
    String? candidateCity,
    String? candidateRegion,
    String? candidateCountry = 'mx',
  }) {
    final profileCurrentPosition = profile?.personalInfo.currentPosition ?? '';
    final profileYearsOfExperience = profile?.personalInfo.yearsOfExperience ?? 0;
    final profileSkills = profile?.skills.items.map((s) => s.name).toList() ?? const [];
    final profileHistoricalRoles = profile?.experience.map((e) => e.role).toList() ?? const [];

    final skillsScore = _calculateSkillsScore(
      vacancySkills: vacancy.skills,
      vacancyTitle: vacancy.title,
      vacancyDescription: vacancy.description,
      profileSkills: profileSkills,
    );

    final experienceScore = _calculateExperienceScore(
      vacancyLevel: vacancy.experienceLevel,
      vacancyTitle: vacancy.title,
      candidateYears: profileYearsOfExperience,
    );

    final titleScore = _calculateTitleScore(
      vacancyTitle: vacancy.title,
      candidatePosition: profileCurrentPosition,
      historicalRoles: profileHistoricalRoles,
    );

    final modalityScore = _calculateModalityScore(
      vacancyModality: vacancy.modality,
      vacancyLocation: vacancy.location,
      candidateCity: candidateCity,
      candidateRegion: candidateRegion,
      candidateCountry: candidateCountry,
    );

    final locationScore = _calculateLocationScore(
      vacancyLocation: vacancy.location,
      vacancyModality: vacancy.modality,
      candidateCity: candidateCity,
      candidateRegion: candidateRegion,
      candidateCountry: candidateCountry,
    );

    final rawOverall = (skillsScore * weightSkills) +
        (experienceScore * weightExperience) +
        (titleScore * weightTitle) +
        (modalityScore * weightModality) +
        (locationScore * weightLocation);

    final overall = rawOverall.round().clamp(0, 100);

    return LiaMatchBreakdown(
      overall: overall,
      skillsScore: skillsScore,
      experienceScore: experienceScore,
      titleScore: titleScore,
      modalityScore: modalityScore,
      locationScore: locationScore,
    );
  }

  // ── 1. SKILLS (35%) ───────────────────────────────────────────
  static int _calculateSkillsScore({
    required List<String> vacancySkills,
    required String vacancyTitle,
    required String vacancyDescription,
    required List<String> profileSkills,
  }) {
    if (profileSkills.isEmpty) {
      return 60;
    }

    final normProfileSkills = profileSkills
        .map(_normalize)
        .where((s) => s.isNotEmpty)
        .toSet();

    if (vacancySkills.isEmpty) {
      final textToScan = _normalize('$vacancyTitle $vacancyDescription');
      int foundCount = 0;
      for (final skill in normProfileSkills) {
        if (textToScan.contains(skill)) {
          foundCount++;
        }
      }
      if (foundCount >= 4) return 90;
      if (foundCount >= 2) return 80;
      if (foundCount >= 1) return 75;
      return 70;
    }

    final normVacancySkills = vacancySkills
        .map(_normalize)
        .where((s) => s.isNotEmpty)
        .toList();

    if (normVacancySkills.isEmpty) return 70;

    int matchedCount = 0;
    for (final vs in normVacancySkills) {
      if (normProfileSkills.contains(vs)) {
        matchedCount++;
        continue;
      }
      bool matched = false;
      for (final ps in normProfileSkills) {
        if (_areSkillsEquivalent(vs, ps)) {
          matched = true;
          break;
        }
      }
      if (matched) matchedCount++;
    }

    final ratio = matchedCount / normVacancySkills.length;
    return (ratio * 100).round().clamp(0, 100);
  }

  // ── 2. EXPERIENCIA / SENIORITY (25%) ──────────────────────────
  static int _calculateExperienceScore({
    required String vacancyLevel,
    required String vacancyTitle,
    required int candidateYears,
  }) {
    final targetLevel = _detectSeniorityLevel(vacancyLevel, vacancyTitle);
    final candidateLevel = _yearsToSeniorityLevel(candidateYears);

    if (targetLevel == null) {
      return 80;
    }

    final diff = candidateLevel - targetLevel;
    if (diff == 0) {
      return 100;
    }
    if (diff > 0) {
      return (95 - (diff * 5)).clamp(85, 95);
    }
    if (diff == -1) return 65;
    if (diff == -2) return 35;
    return 15;
  }

  static int? _detectSeniorityLevel(String level, String title) {
    final text = _normalize('$level $title');
    if (text.contains('lead') ||
        text.contains('principal') ||
        text.contains('director') ||
        text.contains('head') ||
        text.contains('manager') ||
        text.contains('gerente')) {
      return 4;
    }
    if (text.contains('senior') ||
        text.contains('sr') ||
        text.contains('sr.') ||
        text.contains('avanzado')) {
      return 3;
    }
    if (text.contains('semi-senior') ||
        text.contains('semi senior') ||
        text.contains('ssr') ||
        text.contains('mid') ||
        text.contains('intermedio')) {
      return 2;
    }
    if (text.contains('junior') ||
        text.contains('jr') ||
        text.contains('jr.') ||
        text.contains('trainee') ||
        text.contains('practicante') ||
        text.contains('entry') ||
        text.contains('intern')) {
      return 1;
    }
    return null;
  }

  static int _yearsToSeniorityLevel(int years) {
    if (years <= 1) return 1;
    if (years <= 4) return 2;
    if (years <= 7) return 3;
    return 4;
  }

  // ── 3. TÍTULO / PUESTO (20%) ───────────────────────────────────
  static int _calculateTitleScore({
    required String vacancyTitle,
    required String candidatePosition,
    required List<String> historicalRoles,
  }) {
    if (candidatePosition.trim().isEmpty && historicalRoles.isEmpty) {
      return 70;
    }

    final normVacancy = _normalize(vacancyTitle);
    final vTokens = _tokenizeRole(normVacancy);
    if (vTokens.isEmpty) return 70;

    int maxScore = 0;
    final allRoles = [candidatePosition, ...historicalRoles]
        .where((r) => r.trim().isNotEmpty);

    for (final role in allRoles) {
      final normRole = _normalize(role);
      final rTokens = _tokenizeRole(normRole);
      if (rTokens.isEmpty) continue;

      int matches = 0;
      for (final vt in vTokens) {
        for (final rt in rTokens) {
          if (vt == rt || _areRoleTokensEquivalent(vt, rt)) {
            matches++;
            break;
          }
        }
      }

      final score = ((matches / vTokens.length) * 100).round();
      maxScore = max(maxScore, score);
    }

    if (maxScore >= 70) return 95;
    if (maxScore >= 40) return 80;
    if (maxScore >= 20) return 55;
    return 25;
  }

  static Set<String> _tokenizeRole(String role) {
    const stopwords = {
      'de', 'en', 'el', 'la', 'los', 'las', 'un', 'una', 'para', 'por', 'con',
      'and', 'or', 'for', 'in', 'at', 'the', 'a', 'an', 'of', 'to', 'with',
      'i', 'ii', 'iii', 'iv', 'v', '1', '2', '3', 'jr', 'sr', 'mid', 'senior',
      'junior', 'lead', 'remote', 'remoto', 'mexico', 'mx'
    };

    return role
        .split(RegExp(r'[\s,/\-_|()]+'))
        .map((t) => t.trim())
        .where((t) => t.length > 1 && !stopwords.contains(t))
        .toSet();
  }

  static bool _areRoleTokensEquivalent(String t1, String t2) {
    if (t1 == t2) return true;
    if (t1.contains(t2) || t2.contains(t1)) return true;

    const equivalents = [
      {'developer', 'desarrollador', 'programmer', 'programador', 'software'},
      {'engineer', 'ingeniero', 'ing'},
      {'architect', 'arquitecto'},
      {'analyst', 'analista'},
      {'manager', 'gerente', 'lead', 'jefe'},
      {'administrator', 'administrador', 'admin'},
      {'coordinator', 'coordinador'},
      {'specialist', 'especialista'},
      {'consultant', 'consultor'},
      {'recruiter', 'reclutador', 'talent', 'rh', 'hr'},
    ];

    for (final eq in equivalents) {
      if (eq.contains(t1) && eq.contains(t2)) return true;
    }
    return false;
  }

  // ── 4. MODALIDAD (10%) ─────────────────────────────────────────
  static int _calculateModalityScore({
    required String vacancyModality,
    required String vacancyLocation,
    String? candidateCity,
    String? candidateRegion,
    String? candidateCountry,
  }) {
    final mod = _normalize(vacancyModality);
    final loc = _normalize(vacancyLocation);

    final isRemote = mod.contains('remote') ||
        mod.contains('remoto') ||
        loc.contains('remote') ||
        loc.contains('remoto');

    if (isRemote) {
      return 100;
    }

    final city = _normalize(candidateCity ?? '');
    final region = _normalize(candidateRegion ?? '');

    final isHybrid = mod.contains('hybrid') || mod.contains('hibrido');
    if (isHybrid) {
      if (city.isNotEmpty && loc.contains(city)) return 95;
      if (region.isNotEmpty && loc.contains(region)) return 85;
      return 70;
    }

    if (city.isNotEmpty && loc.contains(city)) return 100;
    if (region.isNotEmpty && loc.contains(region)) return 75;
    if (loc.contains('mexico') || loc.contains('mx')) return 55;
    return 40;
  }

  // ── 5. UBICACIÓN (10%) ─────────────────────────────────────────
  static int _calculateLocationScore({
    required String vacancyLocation,
    required String vacancyModality,
    String? candidateCity,
    String? candidateRegion,
    String? candidateCountry,
  }) {
    final loc = _normalize(vacancyLocation);
    final mod = _normalize(vacancyModality);

    final isRemote = mod.contains('remote') ||
        mod.contains('remoto') ||
        loc.contains('remote') ||
        loc.contains('remoto');

    if (isRemote) {
      return 95;
    }

    final city = _normalize(candidateCity ?? '');
    final region = _normalize(candidateRegion ?? '');

    if (city.isNotEmpty && loc.contains(city)) {
      return 100;
    }
    if (region.isNotEmpty && loc.contains(region)) {
      return 85;
    }
    if (loc.contains('mexico') || loc.contains('mx') || loc.isNotEmpty) {
      return 70;
    }
    return 50;
  }

  static String _normalize(String text) {
    return text
        .toLowerCase()
        .replaceAll('á', 'a')
        .replaceAll('é', 'e')
        .replaceAll('í', 'i')
        .replaceAll('ó', 'o')
        .replaceAll('ú', 'u')
        .replaceAll('ü', 'u')
        .replaceAll('ñ', 'n')
        .trim();
  }

  static bool _areSkillsEquivalent(String s1, String s2) {
    if (s1 == s2) return true;
    if (s1.contains(s2) || s2.contains(s1)) return true;

    const aliases = [
      {'js', 'javascript'},
      {'ts', 'typescript'},
      {'py', 'python'},
      {'react', 'reactjs', 'react.js'},
      {'vue', 'vuejs', 'vue.js'},
      {'node', 'nodejs', 'node.js'},
      {'k8s', 'kubernetes'},
      {'golang', 'go'},
      {'flutter', 'dart'},
      {'aws', 'amazon web services'},
      {'gcp', 'google cloud'},
      {'azure', 'microsoft azure'},
      {'ci/cd', 'cicd', 'continuous integration'},
      {'qa', 'quality assurance', 'testing'},
    ];

    for (final group in aliases) {
      if (group.contains(s1) && group.contains(s2)) return true;
    }
    return false;
  }
}
