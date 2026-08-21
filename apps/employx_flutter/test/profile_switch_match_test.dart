import 'package:flutter_test/flutter_test.dart';
import 'package:employx_flutter/core/models/professional_profile_model.dart';
import 'package:employx_flutter/features/vacancies/models/vacancy_model.dart';
import 'package:employx_flutter/features/vacancies/services/lia_match_calculator.dart';

void main() {
  group('Sincronización de CV activo y Recálculo de Match LIA', () {
    // Vacantes en memoria (las mismas para ambos perfiles)
    final vacancies = [
      const VacancyModel(
        id: 'v-dev',
        title: 'Senior Flutter Developer',
        company: 'Tech Corp',
        location: 'Piedras Negras, Coahuila, Mexico',
        modality: 'Presencial',
        experienceLevel: 'Senior',
        skills: ['Flutter', 'Dart', 'Docker', 'Git'],
      ),
      const VacancyModel(
        id: 'v-acc',
        title: 'Contador General / Auditor',
        company: 'Finanzas Norte',
        location: 'Piedras Negras, Coahuila, Mexico',
        modality: 'Presencial',
        experienceLevel: 'Senior',
        skills: ['Contabilidad', 'SAP', 'Impuestos', 'Auditoría'],
      ),
      const VacancyModel(
        id: 'v-data',
        title: 'Python Data Engineer',
        company: 'Global Data',
        location: 'Remote, Mexico',
        modality: 'Remote',
        experienceLevel: 'Mid',
        skills: ['Python', 'FastAPI', 'SQL'],
      ),
    ];

    // Perfil A: Desarrollador Flutter Senior
    final profileA = const ProfessionalProfile(
      id: 'profile-a-dev',
      personalInfo: PersonalInfo(
        name: 'Ana Dev',
        currentPosition: 'Senior Flutter Developer',
        yearsOfExperience: 6,
        location: 'Piedras Negras, Coahuila, México',
      ),
      skills: Skills(
        items: [
          Skill(name: 'Flutter', category: 'technical'),
          Skill(name: 'Dart', category: 'technical'),
          Skill(name: 'Docker', category: 'technical'),
          Skill(name: 'Git', category: 'technical'),
        ],
      ),
      experience: [
        Experience(company: 'App Corp', role: 'Flutter Developer'),
      ],
      atsMetrics: ATSMetrics(),
      linkedinMetrics: LinkedInMetrics(),
      careerMetrics: CareerMetrics(),
    );

    // Perfil B: Contador Senior
    final profileB = const ProfessionalProfile(
      id: 'profile-b-acc',
      personalInfo: PersonalInfo(
        name: 'Carlos Contador',
        currentPosition: 'Contador Senior',
        yearsOfExperience: 7,
        location: 'Piedras Negras, Coahuila, México',
      ),
      skills: Skills(
        items: [
          Skill(name: 'Contabilidad', category: 'technical'),
          Skill(name: 'SAP', category: 'technical'),
          Skill(name: 'Impuestos', category: 'technical'),
          Skill(name: 'Auditoría', category: 'technical'),
        ],
      ),
      experience: [
        Experience(company: 'Despacho Contable', role: 'Contador General'),
      ],
      atsMetrics: ATSMetrics(),
      linkedinMetrics: LinkedInMetrics(),
      careerMetrics: CareerMetrics(),
    );

    test('Cambio de CV activo recalcula Match y reordena vacantes en memoria', () {
      // 1. Evaluación con Perfil A (Desarrollador)
      final scoredA = vacancies.map((v) {
        final breakdown = LiaMatchCalculator.calculate(
          vacancy: v,
          profile: profileA,
          candidateCity: 'Piedras Negras',
          candidateRegion: 'Coahuila',
        );
        return (id: v.id, title: v.title, match: breakdown.overall);
      }).toList();

      scoredA.sort((a, b) => b.match.compareTo(a.match));

      print('Scores con Perfil A (Dev):');
      for (final s in scoredA) {
        print('  ${s.match}% -> ${s.title}');
      }

      // Vacante de Flutter debe ser la #1 para Perfil A
      expect(scoredA.first.id, equals('v-dev'));
      expect(scoredA.first.match, greaterThanOrEqualTo(90));
      // Vacante de Contador debe tener score bajo para Perfil A
      final accMatchInA = scoredA.firstWhere((s) => s.id == 'v-acc').match;
      expect(accMatchInA, lessThan(60));

      // 2. Cambio a Perfil B (Contador) sin consultar de nuevo la API
      final scoredB = vacancies.map((v) {
        final breakdown = LiaMatchCalculator.calculate(
          vacancy: v,
          profile: profileB,
          candidateCity: 'Piedras Negras',
          candidateRegion: 'Coahuila',
        );
        return (id: v.id, title: v.title, match: breakdown.overall);
      }).toList();

      scoredB.sort((a, b) => b.match.compareTo(a.match));

      print('\nScores con Perfil B (Contador):');
      for (final s in scoredB) {
        print('  ${s.match}% -> ${s.title}');
      }

      // Vacante de Contador debe ser la #1 para Perfil B
      expect(scoredB.first.id, equals('v-acc'));
      expect(scoredB.first.match, greaterThanOrEqualTo(90));
      // Vacante de Flutter debe tener score bajo para Perfil B
      final devMatchInB = scoredB.firstWhere((s) => s.id == 'v-dev').match;
      expect(devMatchInB, lessThan(60));
    });
  });
}
