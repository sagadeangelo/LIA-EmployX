import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_glass_panel.dart';

import '../providers/profile_hub_provider.dart';

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

    final profileHub =
        context.watch<ProfileHubProvider>();

    final profile =
        profileHub.activeProfessionalProfile;

    // ============================================================
    // LOADING
    // ============================================================

    if (profileHub.isLoadingProfile) {
      return Scaffold(
        backgroundColor: colors.background,
        body: Center(
          child: LiaGlassPanel(
            hasGlow: true,
            glowColor: colors.accentPrimary,
            padding: EdgeInsets.all(
              spacings.xxl,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                SizedBox(
                  width: 42,
                  height: 42,
                  child: CircularProgressIndicator(
                    color: colors.accentPrimary,
                    strokeWidth: 2.5,
                  ),
                ),
                SizedBox(
                  height: spacings.lg,
                ),
                Text(
                  'Cargando perfil profesional...',
                  style:
                      context.liaTypography.h3.copyWith(
                    color: colors.textPrimary,
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    // ============================================================
    // EMPTY / ERROR
    // ============================================================

    if (profile == null) {
      return _buildEmptyState(
        context,
        profileHub,
      );
    }

    // ============================================================
    // PROFESSIONAL PROFILE
    // ============================================================

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
                  colors.background.withValues(
                    alpha: 0.95,
                  ),
                  const Color(0xFF0D1B2A),
                ],
              ),
            ),
          ),

          CustomScrollView(
            slivers: [
              SliverPadding(
                padding: EdgeInsets.all(
                  spacings.xl,
                ),
                sliver: SliverList(
                  delegate:
                      SliverChildListDelegate([
                    ProfileHeroHeader(
                      profile: profile,
                    ),

                    SizedBox(
                      height: spacings.xl,
                    ),

                    ProfileSummaryWidget(
                      profile: profile,
                    ),

                    SizedBox(
                      height: spacings.xl,
                    ),

                    ProfileMetricsRadarWidget(
                      profile: profile,
                    ),

                    SizedBox(
                      height: spacings.xl,
                    ),

                    ProfileTimelineWidget(
                      profile: profile,
                    ),

                    SizedBox(
                      height: spacings.xl,
                    ),

                    ProfileSkillsWidget(
                      profile: profile,
                    ),

                    SizedBox(
                      height: spacings.xl,
                    ),

                    ProfileEducationCertificationsWidget(
                      profile: profile,
                    ),

                    SizedBox(
                      height: spacings.xxl,
                    ),
                  ]),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(
    BuildContext context,
    ProfileHubProvider profileHub,
  ) {
    final colors = context.liaColors;
    final typography =
        context.liaTypography;
    final spacings =
        context.liaSpacings;

    final hasCvs = profileHub.hasCvs;

    final error =
        profileHub.profileError;

    return Scaffold(
      backgroundColor: colors.background,
      body: Center(
        child: LiaGlassPanel(
          hasGlow: true,
          glowColor: colors.accentPrimary,
          padding: EdgeInsets.all(
            spacings.xxl,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                hasCvs
                    ? Icons.description_outlined
                    : Icons.person_search_outlined,
                size: 64,
                color: colors.accentPrimary,
              ),

              SizedBox(
                height: spacings.lg,
              ),

              Text(
                hasCvs
                    ? 'Perfil Profesional No Disponible'
                    : 'Perfil No Encontrado',
                style: typography.h2.copyWith(
                  color: colors.textPrimary,
                ),
                textAlign: TextAlign.center,
              ),

              SizedBox(
                height: spacings.sm,
              ),

              Text(
                hasCvs
                    ? (
                        error ??
                        'El CV seleccionado todavía no tiene '
                        'un perfil profesional disponible.'
                      )
                    : (
                        'Aún no hay un perfil procesado.\n'
                        'Ve al Centro de Comando y sube tu CV '
                        'para comenzar.'
                      ),
                textAlign: TextAlign.center,
                style:
                    typography.bodyMedium.copyWith(
                  color: colors.textSecondary,
                ),
              ),

              if (hasCvs) ...[
                SizedBox(
                  height: spacings.lg,
                ),
                TextButton.icon(
                  onPressed:
                      profileHub
                          .refreshActiveProfessionalProfile,
                  icon: const Icon(
                    Icons.refresh,
                  ),
                  label: const Text(
                    'Reintentar',
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}