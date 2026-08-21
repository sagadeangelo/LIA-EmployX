import 'package:flutter_test/flutter_test.dart';
import 'package:employx_flutter/core/models/professional_profile_model.dart';
import 'package:employx_flutter/features/vacancies/models/vacancy_model.dart';
import 'package:employx_flutter/features/vacancies/services/lia_match_calculator.dart';

void main() {
  group('LiaMatchCalculator - Pruebas Obligatorias Fase 2F', () {
    const candidateCity = 'Piedras Negras';
    const candidateRegion = 'Coahuila';
    const profileRole = 'Senior Software Engineer';
    const profileYears = 6;
    const profileSkills = [
      Skill(name: 'Flutter', category: 'technical'),
      Skill(name: 'Dart', category: 'technical'),
      Skill(name: 'Python', category: 'technical'),
      Skill(name: 'FastAPI', category: 'technical'),
      Skill(name: 'Docker', category: 'technical'),
      Skill(name: 'Git', category: 'technical'),
    ];
    const profileRoles = [
      Experience(company: 'A', role: 'Software Engineer'),
      Experience(company: 'B', role: 'Fullstack Developer'),
    ];

    final seniorProfile = ProfessionalProfile(
      id: 'prof-1',
      personalInfo: const PersonalInfo(
        name: 'Dev Senior',
        location: 'Piedras Negras, Coahuila, México',
        currentPosition: profileRole,
        yearsOfExperience: profileYears,
      ),
      skills: const Skills(items: profileSkills),
      experience: profileRoles,
      atsMetrics: const ATSMetrics(),
      linkedinMetrics: const LinkedInMetrics(),
      careerMetrics: const CareerMetrics(),
    );

    test('Caso 1: Vacante muy compatible + Piedras Negras -> Score muy alto (>90)', () {
      final vacancy = const VacancyModel(
        id: 'v1',
        title: 'Sr. Software Engineer',
        company: 'Empresa Local',
        location: 'Piedras Negras, Coahuila, Mexico',
        modality: 'Presencial',
        experienceLevel: 'Senior',
        skills: ['Flutter', 'Dart', 'Docker'],
      );

      final breakdown = LiaMatchCalculator.calculate(
        vacancy: vacancy,
        profile: seniorProfile,
        candidateCity: candidateCity,
        candidateRegion: candidateRegion,
      );

      expect(breakdown.overall, greaterThanOrEqualTo(90));
      expect(breakdown.skillsScore, equals(100));
      expect(breakdown.experienceScore, equals(100));
      expect(breakdown.locationScore, equals(100));
    });

    test('Caso 2: Vacante muy compatible + Remota -> Compite en el top (>90)', () {
      final vacancy = const VacancyModel(
        id: 'v2',
        title: 'Senior Flutter Developer',
        company: 'Remote Tech',
        location: 'Remote, Mexico',
        modality: 'Remote',
        experienceLevel: 'Senior',
        skills: ['Flutter', 'Dart', 'Python'],
      );

      final breakdown = LiaMatchCalculator.calculate(
        vacancy: vacancy,
        profile: seniorProfile,
        candidateCity: candidateCity,
        candidateRegion: candidateRegion,
      );

      expect(breakdown.overall, greaterThanOrEqualTo(90));
      expect(breakdown.modalityScore, equals(100));
      expect(breakdown.locationScore, equals(95));
    });

    test('Caso 3: Vacante poco compatible + Piedras Negras -> NO supera a vacante remota compatible', () {
      final vLocalIncompatible = const VacancyModel(
        id: 'v3',
        title: 'Procurement Manager',
        company: 'Planta Local',
        location: 'Piedras Negras IBU',
        modality: 'Presencial',
        experienceLevel: 'Lead',
        skills: ['SAP', 'Compras', 'Negociación', 'Logística'],
      );

      final vRemoteCompatible = const VacancyModel(
        id: 'v2',
        title: 'Senior Flutter Developer',
        company: 'Remote Tech',
        location: 'Remote, Mexico',
        modality: 'Remote',
        experienceLevel: 'Senior',
        skills: ['Flutter', 'Dart', 'Python'],
      );

      final bLocal = LiaMatchCalculator.calculate(
        vacancy: vLocalIncompatible,
        profile: seniorProfile,
        candidateCity: candidateCity,
        candidateRegion: candidateRegion,
      );

      final bRemote = LiaMatchCalculator.calculate(
        vacancy: vRemoteCompatible,
        profile: seniorProfile,
        candidateCity: candidateCity,
        candidateRegion: candidateRegion,
      );

      expect(bRemote.overall, greaterThan(bLocal.overall));
      expect(bLocal.overall, lessThan(60));
    });

    test('Caso 4: Skills coincidentes pero experiencia insuficiente -> Penaliza seniority', () {
      final juniorProfile = ProfessionalProfile(
        id: 'prof-junior',
        personalInfo: const PersonalInfo(
          name: 'Junior Dev',
          currentPosition: 'Junior Developer',
          yearsOfExperience: 1,
        ),
        skills: const Skills(items: profileSkills),
        experience: const [],
        atsMetrics: const ATSMetrics(),
        linkedinMetrics: const LinkedInMetrics(),
        careerMetrics: const CareerMetrics(),
      );

      final vLead = const VacancyModel(
        id: 'v4',
        title: 'Lead Software Architect',
        company: 'Enterprise Corp',
        location: 'Mexico City, Mexico',
        modality: 'Remote',
        experienceLevel: 'Lead',
        skills: ['Flutter', 'Dart', 'Python', 'FastAPI'],
      );

      final breakdown = LiaMatchCalculator.calculate(
        vacancy: vLead,
        profile: juniorProfile,
        candidateCity: candidateCity,
        candidateRegion: candidateRegion,
      );

      expect(breakdown.skillsScore, equals(100));
      expect(breakdown.experienceScore, equals(15)); // Fuertemente penalizado por 3 niveles de brecha
      expect(breakdown.overall, lessThan(80));
    });

    test('Caso 5: Título muy similar y skills compatibles -> Score alto (>85)', () {
      final vacancy = const VacancyModel(
        id: 'v5',
        title: 'Senior Software Engineer - Mobile',
        company: 'Tech Hub',
        location: 'Monterrey, Nuevo León',
        modality: 'Hybrid',
        experienceLevel: 'Senior',
        skills: ['Flutter', 'Dart', 'Git'],
      );

      final breakdown = LiaMatchCalculator.calculate(
        vacancy: vacancy,
        profile: seniorProfile,
        candidateCity: candidateCity,
        candidateRegion: candidateRegion,
      );

      expect(breakdown.overall, greaterThanOrEqualTo(85));
      expect(breakdown.titleScore, greaterThanOrEqualTo(80));
    });

    test('Caso 6: Perfil con campos parcialmente vacíos -> Sin crash y score determinista en rango', () {
      final emptyProfile = const ProfessionalProfile(
        id: 'prof-empty',
        personalInfo: PersonalInfo(),
        skills: Skills(),
        atsMetrics: ATSMetrics(),
        linkedinMetrics: LinkedInMetrics(),
        careerMetrics: CareerMetrics(),
      );

      final vacancy = const VacancyModel(
        id: 'v6',
        title: 'Software Engineer',
        company: 'Company',
      );

      final breakdown = LiaMatchCalculator.calculate(
        vacancy: vacancy,
        profile: emptyProfile,
      );

      expect(breakdown.overall, inInclusiveRange(0, 100));
      expect(breakdown.skillsScore, inInclusiveRange(0, 100));
      expect(breakdown.experienceScore, inInclusiveRange(0, 100));
      expect(breakdown.titleScore, inInclusiveRange(0, 100));
      expect(breakdown.modalityScore, inInclusiveRange(0, 100));
      expect(breakdown.locationScore, inInclusiveRange(0, 100));
    });
  });
}
