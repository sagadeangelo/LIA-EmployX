import 'package:flutter/material.dart';

import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileTimelineWidget extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileTimelineWidget({
    super.key,
    required this.profile,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final experiences = profile.experience;

    if (experiences.isEmpty) {
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
                Icons.work_history_outlined,
                color: colors.accentPrimary,
                size: 24,
              ),
              SizedBox(
                width: spacings.sm,
              ),
              Text(
                'Experiencia Profesional',
                style: typography.h3.copyWith(
                  color: colors.textPrimary,
                ),
              ),
            ],
          ),

          SizedBox(
            height: spacings.lg,
          ),

          for (int index = 0;
              index < experiences.length;
              index++)
            _buildTimelineItem(
              context,
              experiences[index],
              isLast:
                  index == experiences.length - 1,
            ),
        ],
      ),
    );
  }

  Widget _buildTimelineItem(
    BuildContext context,
    Experience experience, {
    required bool isLast,
  }) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final role =
        experience.role.trim().isNotEmpty
            ? experience.role.trim()
            : 'Rol no especificado';

    final company =
        experience.company.trim().isNotEmpty
            ? experience.company.trim()
            : 'Empresa no especificada';

    final startDate =
        experience.startDate.trim();

    final endDate =
        experience.endDate.trim();

    final description =
        experience.description.trim();

    final achievements =
        experience.achievements
            .where(
              (achievement) =>
                  achievement.trim().isNotEmpty,
            )
            .map(
              (achievement) =>
                  achievement.trim(),
            )
            .toList();

    final period = _buildPeriod(
      startDate,
      endDate,
    );

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          _buildTimelineIndicator(
            context,
            isLast: isLast,
          ),

          SizedBox(
            width: spacings.md,
          ),

          Expanded(
            child: Padding(
              padding:
                  EdgeInsets.only(
                bottom:
                    isLast ? 0 : 32,
              ),
              child: Column(
                crossAxisAlignment:
                    CrossAxisAlignment.start,
                children: [
                  Text(
                    role,
                    style:
                        typography.h3.copyWith(
                      color:
                          colors.textPrimary,
                      fontSize: 18,
                    ),
                  ),

                  const SizedBox(
                    height: 4,
                  ),

                  Text(
                    period.isEmpty
                        ? company
                        : '$company • $period',
                    style:
                        typography.bodyMedium
                            .copyWith(
                      color:
                          colors.accentTertiary,
                      fontWeight:
                          FontWeight.w500,
                    ),
                  ),

                  if (description
                      .isNotEmpty) ...[
                    SizedBox(
                      height: spacings.sm,
                    ),

                    Text(
                      description,
                      style:
                          typography.bodyMedium
                              .copyWith(
                        color:
                            colors.textSecondary,
                        height: 1.5,
                      ),
                    ),
                  ],

                  if (achievements
                      .isNotEmpty) ...[
                    SizedBox(
                      height: spacings.sm,
                    ),

                    _buildAchievements(
                      context,
                      achievements,
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimelineIndicator(
    BuildContext context, {
    required bool isLast,
  }) {
    final colors = context.liaColors;

    return SizedBox(
      width: 14,
      child: Column(
        children: [
          Container(
            margin:
                const EdgeInsets.only(
              top: 4,
            ),
            width: 14,
            height: 14,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color:
                    colors.accentPrimary,
                width: 3,
              ),
              color:
                  colors.background,
            ),
          ),

          if (!isLast)
            Expanded(
              child: Container(
                width: 2,
                color: colors.border,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildAchievements(
    BuildContext context,
    List<String> achievements,
  ) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    return Column(
      crossAxisAlignment:
          CrossAxisAlignment.start,
      children: [
        for (final achievement
            in achievements)
          Padding(
            padding:
                const EdgeInsets.only(
              bottom: 5,
            ),
            child: Row(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                Text(
                  '✓',
                  style:
                      typography.bodyMedium
                          .copyWith(
                    color:
                        colors.accentPrimary,
                    fontWeight:
                        FontWeight.bold,
                  ),
                ),

                const SizedBox(
                  width: 8,
                ),

                Expanded(
                  child: Text(
                    achievement,
                    style:
                        typography.bodyMedium
                            .copyWith(
                      color:
                          colors.textSecondary,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  String _buildPeriod(
    String startDate,
    String endDate,
  ) {
    if (startDate.isEmpty &&
        endDate.isEmpty) {
      return '';
    }

    if (startDate.isEmpty) {
      return endDate;
    }

    if (endDate.isEmpty) {
      return '$startDate – Present';
    }

    return '$startDate – $endDate';
  }
}