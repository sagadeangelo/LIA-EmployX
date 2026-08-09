import 'package:flutter/material.dart';

import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileSkillsWidget extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileSkillsWidget({
    super.key,
    required this.profile,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final technicalSkills =
        profile.skills.technicalSkills;

    final softSkills =
        profile.skills.softSkills;

    if (technicalSkills.isEmpty &&
        softSkills.isEmpty) {
      return const SizedBox.shrink();
    }

    return LiaGlassPanel(
      padding: EdgeInsets.all(
        spacings.xl,
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.psychology_outlined,
                color: colors.accentPrimary,
                size: 24,
              ),
              SizedBox(
                width: spacings.sm,
              ),
              Text(
                'Habilidades (Skills)',
                style: typography.h3.copyWith(
                  color: colors.textPrimary,
                ),
              ),
            ],
          ),

          SizedBox(
            height: spacings.lg,
          ),

          if (technicalSkills.isNotEmpty)
            _buildSkillGroup(
              context,
              title: 'Technical Skills',
              skills: technicalSkills,
              isTechnical: true,
            ),

          if (technicalSkills.isNotEmpty &&
              softSkills.isNotEmpty)
            SizedBox(
              height: spacings.lg,
            ),

          if (softSkills.isNotEmpty)
            _buildSkillGroup(
              context,
              title: 'Soft Skills',
              skills: softSkills,
              isTechnical: false,
            ),
        ],
      ),
    );
  }

  Widget _buildSkillGroup(
    BuildContext context, {
    required String title,
    required List<String> skills,
    required bool isTechnical,
  }) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: typography.caption.copyWith(
            color: colors.textMuted,
          ),
        ),

        SizedBox(
          height: spacings.sm,
        ),

        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final skill in skills)
              _buildChip(
                context,
                skill,
                isTechnical: isTechnical,
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildChip(
    BuildContext context,
    String label, {
    required bool isTechnical,
  }) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    final accentColor = isTechnical
        ? colors.accentPrimary
        : colors.accentTertiary;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 6,
      ),
      decoration: BoxDecoration(
        color: accentColor.withValues(
          alpha: 0.1,
        ),
        borderRadius:
            BorderRadius.circular(16),
        border: Border.all(
          color: accentColor.withValues(
            alpha: 0.3,
          ),
        ),
      ),
      child: Text(
        label,
        style: typography.bodyMedium.copyWith(
          color: accentColor,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}