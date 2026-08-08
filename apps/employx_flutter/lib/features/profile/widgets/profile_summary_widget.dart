import 'package:flutter/material.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileSummaryWidget extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileSummaryWidget({Key? key, required this.profile}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final summary = profile.personalInfo.professionalSummary;

    if (summary.isEmpty) return const SizedBox.shrink();

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.format_quote, color: colors.accentPrimary, size: 24),
              SizedBox(width: spacings.sm),
              Text('Resumen Profesional', style: typography.h3.copyWith(color: colors.textPrimary)),
            ],
          ),
          SizedBox(height: spacings.md),
          Text(
            summary,
            style: typography.bodyMedium.copyWith(
              color: colors.textSecondary,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
}
