import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/lia_theme.dart';
import '../../../core/actions/mission_actions.dart';
import '../../../core/ui/lia_glass_panel.dart';

import '../widgets/ats_analyzer_panel.dart';
import '../widgets/profile_hero_header.dart';
import '../widgets/profile_summary_widget.dart';
import '../widgets/profile_metrics_radar_widget.dart';
import '../widgets/profile_timeline_widget.dart';
import '../widgets/profile_skills_widget.dart';
import '../widgets/profile_education_certifications_widget.dart';

class ProfessionalProfileScreen extends StatelessWidget {
  const ProfessionalProfileScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;

    final missionActions = context.watch<MissionActions>();
    final profile = missionActions.currentProfile;

    if (profile == null) {
      return _buildEmptyState(context);
    }

    return Scaffold(
      backgroundColor: colors.background,
      body: Stack(
        children: [
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  colors.background,
                  colors.background.withValues(alpha: 0.95),
                  const Color(0xFF0D1B2A),
                ],
              ),
            ),
          ),
          CustomScrollView(
            slivers: [
              SliverPadding(
                padding: EdgeInsets.all(spacings.xl),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    ProfileHeroHeader(profile: profile),
                    SizedBox(height: spacings.xl),
                    ProfileSummaryWidget(profile: profile),
                    SizedBox(height: spacings.xl),
                    ATSAnalyzerPanel(profile: profile),
                    SizedBox(height: spacings.xl),
                    ProfileMetricsRadarWidget(profile: profile),
                    SizedBox(height: spacings.xl),
                    ProfileTimelineWidget(profile: profile),
                    SizedBox(height: spacings.xl),
                    ProfileSkillsWidget(profile: profile),
                    SizedBox(height: spacings.xl),
                    ProfileEducationCertificationsWidget(profile: profile),
                    SizedBox(height: spacings.xxl),
                  ]),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: Center(
        child: LiaGlassPanel(
          hasGlow: true,
          glowColor: colors.accentPrimary,
          padding: EdgeInsets.all(spacings.xxl),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.person_search_outlined,
                size: 64,
                color: colors.accentPrimary,
              ),
              SizedBox(height: spacings.lg),
              Text(
                'Perfil No Encontrado',
                style: typography.h2.copyWith(color: colors.textPrimary),
              ),
              SizedBox(height: spacings.sm),
              Text(
                'Aún no hay un perfil procesado.\n'
                'Ve al Centro de Comando y sube tu CV para comenzar.',
                textAlign: TextAlign.center,
                style: typography.bodyMedium.copyWith(color: colors.textSecondary),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
