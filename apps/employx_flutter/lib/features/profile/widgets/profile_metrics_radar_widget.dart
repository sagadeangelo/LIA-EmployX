import 'package:flutter/material.dart';

import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileMetricsRadarWidget extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileMetricsRadarWidget({
    super.key,
    required this.profile,
  });

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;

    final ats = profile.atsMetrics;
    final linkedin = profile.linkedinMetrics;
    final career = profile.careerMetrics;

    return LayoutBuilder(
      builder: (context, constraints) {
        final isCompact =
            constraints.maxWidth < 900;

        final cards = [
          _buildMetricCard(
            context,
            title: 'ATS Analyzer',
            icon: Icons.document_scanner_outlined,
            score: ats.atsScore,
            color: colors.success,
            recommendations:
                ats.missingKeywords,
            recTitle: 'Keywords Sugeridas',
          ),
          _buildMetricCard(
            context,
            title: 'LinkedIn Optimizer',
            icon: Icons.work_outline,
            score: linkedin.score,
            color: colors.accentTertiary,
            recommendations:
                linkedin.recommendations,
            recTitle:
                'Recomendaciones LinkedIn',
          ),
          _buildCareerHealthCard(
            context,
            career: career,
          ),
        ];

        if (isCompact) {
          return Column(
            children: [
              for (int i = 0;
                  i < cards.length;
                  i++) ...[
                cards[i],
                if (i < cards.length - 1)
                  SizedBox(
                    height: spacings.lg,
                  ),
              ],
            ],
          );
        }

        return Row(
          crossAxisAlignment:
              CrossAxisAlignment.start,
          children: [
            Expanded(
              child: cards[0],
            ),
            SizedBox(
              width: spacings.lg,
            ),
            Expanded(
              child: cards[1],
            ),
            SizedBox(
              width: spacings.lg,
            ),
            Expanded(
              child: cards[2],
            ),
          ],
        );
      },
    );
  }

  Widget _buildCareerHealthCard(
    BuildContext context, {
    required dynamic career,
  }) {
    final level =
        career.employabilityLevel
            .toString()
            .trim();

    final normalizedLevel =
        level.toLowerCase();

    final visualScore =
        _careerVisualScore(
      normalizedLevel,
    );

    final color =
        _careerColor(
      context,
      normalizedLevel,
    );

    return _buildMetricCard(
      context,
      title: 'Career Health',
      icon:
          Icons.monitor_heart_outlined,
      score: visualScore,
      color: color,
      recommendations:
          career.areasForImprovement,
      recTitle:
          level.isEmpty
              ? 'Estado Profesional'
              : 'Nivel: $level',
    );
  }

  Widget _buildMetricCard(
    BuildContext context, {
    required String title,
    required IconData icon,
    required int score,
    required Color color,
    required List<String> recommendations,
    required String recTitle,
  }) {
    final colors = context.liaColors;
    final typography =
        context.liaTypography;
    final spacings =
        context.liaSpacings;

    final safeScore =
        score.clamp(0, 100);

    final visibleRecommendations =
        recommendations
            .where(
              (item) =>
                  item.trim().isNotEmpty,
            )
            .take(4)
            .toList();

    return LiaGlassPanel(
      padding: EdgeInsets.all(
        spacings.xl,
      ),
      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment:
                MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Row(
                  children: [
                    Icon(
                      icon,
                      size: 20,
                      color: color,
                    ),

                    const SizedBox(
                      width: 8,
                    ),

                    Expanded(
                      child: Text(
                        title,
                        maxLines: 1,
                        overflow:
                            TextOverflow.ellipsis,
                        style: typography
                            .bodyMedium
                            .copyWith(
                          color:
                              colors.textPrimary,
                          fontWeight:
                              FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(
                width: 12,
              ),

              Text(
                '$safeScore',
                style: typography.h2.copyWith(
                  color: color,
                ),
              ),
            ],
          ),

          SizedBox(
            height: spacings.md,
          ),

          ClipRRect(
            borderRadius:
                BorderRadius.circular(4),
            child:
                LinearProgressIndicator(
              value:
                  safeScore / 100.0,
              backgroundColor:
                  colors.surfaceHover,
              valueColor:
                  AlwaysStoppedAnimation<
                      Color>(
                color,
              ),
              minHeight: 8,
            ),
          ),

          SizedBox(
            height: spacings.lg,
          ),

          Text(
            recTitle,
            style:
                typography.caption.copyWith(
              color: colors.textMuted,
            ),
          ),

          SizedBox(
            height: spacings.sm,
          ),

          if (visibleRecommendations
              .isEmpty)
            Text(
              'No hay recomendaciones crÃ­ticas.',
              style:
                  typography.bodySmall
                      .copyWith(
                color:
                    colors.textSecondary,
              ),
            )
          else
            for (final recommendation
                in visibleRecommendations)
              Padding(
                padding:
                    const EdgeInsets.only(
                  bottom: 6,
                ),
                child: Row(
                  crossAxisAlignment:
                      CrossAxisAlignment
                          .start,
                  children: [
                    Icon(
                      Icons.arrow_right,
                      size: 16,
                      color: color,
                    ),

                    const SizedBox(
                      width: 4,
                    ),

                    Expanded(
                      child: Text(
                        recommendation,
                        style: typography
                            .bodySmall
                            .copyWith(
                          color:
                              colors.textSecondary,
                        ),
                        maxLines: 2,
                        overflow:
                            TextOverflow
                                .ellipsis,
                      ),
                    ),
                  ],
                ),
              ),
        ],
      ),
    );
  }

  int _careerVisualScore(
    String level,
  ) {
    switch (level) {
      case 'high':
        return 100;

      case 'medium':
        return 60;

      case 'low':
        return 30;

      default:
        return 0;
    }
  }

  Color _careerColor(
    BuildContext context,
    String level,
  ) {
    final colors = context.liaColors;

    switch (level) {
      case 'high':
        return colors.success;

      case 'medium':
        return colors.accentTertiary;

      case 'low':
        return colors.accentPrimary;

      default:
        return colors.textMuted;
    }
  }
}
