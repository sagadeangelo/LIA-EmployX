import 'package:flutter/material.dart';

import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileHeroHeader extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileHeroHeader({
    super.key,
    required this.profile,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;

    final name = profile.personalInfo.name.isNotEmpty
        ? profile.personalInfo.name
        : 'Candidato';

    final role = profile.personalInfo.currentPosition.isNotEmpty
        ? profile.personalInfo.currentPosition
        : profile.experience.isNotEmpty
            ? profile.experience.first.role
            : 'Profesional en Búsqueda';

    final location = profile.personalInfo.location;

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildAvatar(context, name),
              SizedBox(width: spacings.xl),
              Expanded(
                child: _buildIdentity(
                  context,
                  name: name,
                  role: role,
                  location: location,
                ),
              ),
              SizedBox(width: spacings.lg),
              _buildActions(context),
            ],
          ),

          Divider(
            color: colors.border,
            height: spacings.xxl,
          ),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildTopMetric(
                context,
                'Experiencia',
                '${profile.personalInfo.yearsOfExperience} años',
                Icons.timer_outlined,
              ),
              _buildTopMetric(
                context,
                'ATS Score',
                '${profile.atsMetrics.atsScore}',
                Icons.document_scanner_outlined,
                color: colors.success,
              ),
              _buildTopMetric(
                context,
                'LinkedIn Score',
                '${profile.linkedinMetrics.score}',
                Icons.work_outline,
                color: colors.accentTertiary,
              ),
              _buildTopMetric(
                context,
                'Skills',
                '${profile.skills.technicalSkills.length + profile.skills.softSkills.length}',
                Icons.psychology_outlined,
              ),
              _buildTopMetric(
                context,
                'Idiomas',
                '${profile.languages.length}',
                Icons.language_outlined,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAvatar(
    BuildContext context,
    String name,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    final initials = _buildInitials(name);

    return Container(
      width: 100,
      height: 100,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: colors.surfaceHover,
        border: Border.all(
          color: colors.accentPrimary.withValues(alpha: 0.5),
          width: 3,
        ),
        boxShadow: [
          BoxShadow(
            color: colors.accentPrimary.withValues(alpha: 0.2),
            blurRadius: 15,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Center(
        child: Text(
          initials,
          style: typography.h1.copyWith(
            fontSize: initials.length > 1 ? 30 : 40,
            color: colors.accentPrimary,
          ),
        ),
      ),
    );
  }

  Widget _buildIdentity(
    BuildContext context, {
    required String name,
    required String role,
    required String location,
  }) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          name,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: typography.h1.copyWith(
            color: colors.textPrimary,
            fontSize: 32,
          ),
        ),

        SizedBox(height: spacings.xs),

        Text(
          role,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
          style: typography.h3.copyWith(
            color: colors.accentPrimary,
          ),
        ),

        if (location.isNotEmpty) ...[
          SizedBox(height: spacings.sm),
          Row(
            children: [
              Icon(
                Icons.location_on_outlined,
                size: 16,
                color: colors.textSecondary,
              ),
              SizedBox(width: spacings.xs),
              Flexible(
                child: Text(
                  location,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: typography.bodyMedium.copyWith(
                    color: colors.textSecondary,
                  ),
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildActions(
    BuildContext context,
  ) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        ElevatedButton.icon(
          onPressed: null,
          icon: const Icon(Icons.refresh),
          label: const Text('Actualizar Perfil'),
          style: ElevatedButton.styleFrom(
            backgroundColor: colors.accentPrimary,
            foregroundColor: colors.background,
            disabledBackgroundColor: colors.surfaceHover,
            disabledForegroundColor: colors.textMuted,
          ),
        ),

        SizedBox(height: spacings.sm),

        OutlinedButton.icon(
          onPressed: null,
          icon: const Icon(Icons.download),
          label: const Text('Exportar Perfil'),
          style: OutlinedButton.styleFrom(
            foregroundColor: colors.textPrimary,
            side: BorderSide(color: colors.border),
          ),
        ),
      ],
    );
  }

  Widget _buildTopMetric(
    BuildContext context,
    String label,
    String value,
    IconData icon, {
    Color? color,
  }) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    final activeColor = color ?? colors.accentPrimary;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 16,
              color: activeColor,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: typography.caption.copyWith(
                color: colors.textSecondary,
              ),
            ),
          ],
        ),

        const SizedBox(height: 8),

        Text(
          value,
          style: typography.h2.copyWith(
            color: colors.textPrimary,
          ),
        ),
      ],
    );
  }

  String _buildInitials(String name) {
    final parts = name
        .trim()
        .split(RegExp(r'\s+'))
        .where((part) => part.isNotEmpty)
        .toList();

    if (parts.isEmpty) {
      return 'C';
    }

    if (parts.length == 1) {
      return parts.first.substring(0, 1).toUpperCase();
    }

    return (
      parts.first.substring(0, 1) +
      parts.last.substring(0, 1)
    ).toUpperCase();
  }
}