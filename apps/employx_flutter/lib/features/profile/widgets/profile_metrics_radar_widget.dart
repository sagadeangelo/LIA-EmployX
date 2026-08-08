import 'package:flutter/material.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileMetricsRadarWidget extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileMetricsRadarWidget({Key? key, required this.profile}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: _buildMetricCard(
            context,
            title: 'ATS Analyzer',
            icon: Icons.document_scanner,
            score: profile.atsMetrics.atsScore,
            color: colors.success,
            recommendations: profile.atsMetrics.missingKeywords,
            recTitle: 'Keywords Sugeridas',
          ),
        ),
        SizedBox(width: spacings.lg),
        Expanded(
          child: _buildMetricCard(
            context,
            title: 'LinkedIn Optimizer',
            icon: Icons.work_outline,
            score: profile.linkedinMetrics.score,
            color: colors.accentTertiary,
            recommendations: profile.linkedinMetrics.recommendations,
            recTitle: 'Recomendaciones LinkedIn',
          ),
        ),
        SizedBox(width: spacings.lg),
        Expanded(
          child: _buildMetricCard(
            context,
            title: 'Career Health',
            icon: Icons.monitor_heart_outlined,
            score: profile.careerMetrics.employabilityLevel == 'High' ? 95 : (profile.careerMetrics.employabilityLevel == 'Medium' ? 70 : 40), // Derived score
            color: colors.accentPrimary,
            recommendations: profile.careerMetrics.areasForImprovement,
            recTitle: 'Áreas de Mejora (Gaps)',
          ),
        ),
      ],
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
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(icon, size: 20, color: color),
                  SizedBox(width: 8),
                  Text(title, style: typography.bodyMedium.copyWith(color: colors.textPrimary, fontWeight: FontWeight.w600)),
                ],
              ),
              Text('$score', style: typography.h2.copyWith(color: color)),
            ],
          ),
          SizedBox(height: spacings.md),
          // Progress bar
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: score / 100.0,
              backgroundColor: colors.surfaceHover,
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 8,
            ),
          ),
          SizedBox(height: spacings.lg),
          Text(recTitle, style: typography.caption.copyWith(color: colors.textMuted)),
          SizedBox(height: spacings.sm),
          if (recommendations.isEmpty)
            Text('No hay recomendaciones críticas.', style: typography.bodySmall.copyWith(color: colors.textSecondary))
          else
            ...recommendations.take(4).map((rec) => Padding(
              padding: const EdgeInsets.only(bottom: 6.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.arrow_right, size: 16, color: color),
                  Expanded(
                    child: Text(
                      rec,
                      style: typography.bodySmall.copyWith(color: colors.textSecondary),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            )),
        ],
      ),
    );
  }
}
