import 'package:flutter/material.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileTimelineWidget extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileTimelineWidget({Key? key, required this.profile}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final experiences = profile.experience;

    if (experiences.isEmpty) return const SizedBox.shrink();

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.work_history_outlined, color: colors.accentPrimary, size: 24),
              SizedBox(width: spacings.sm),
              Text('Experiencia Profesional', style: typography.h3.copyWith(color: colors.textPrimary)),
            ],
          ),
          SizedBox(height: spacings.lg),
          ...experiences.asMap().entries.map((entry) {
            int idx = entry.key;
            Experience exp = entry.value;
            bool isLast = idx == experiences.length - 1;

            return _buildTimelineItem(context, exp, isLast);
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildTimelineItem(BuildContext context, Experience exp, bool isLast) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline line and dot
          Column(
            children: [
              Container(
                margin: const EdgeInsets.only(top: 4),
                width: 14,
                height: 14,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: colors.accentPrimary, width: 3),
                  color: colors.background,
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
        SizedBox(width: spacings.md),
        // Content
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(bottom: 32.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(exp.role.isNotEmpty ? exp.role : 'Rol no especificado', style: typography.h3.copyWith(color: colors.textPrimary, fontSize: 18)),
                SizedBox(height: 4),
                Text(
                  '${exp.company.isNotEmpty ? exp.company : "Empresa no especificada"} • ${exp.startDate.isNotEmpty ? exp.startDate : "Inicio no disponible"} - ${exp.endDate.isNotEmpty ? exp.endDate : "Fin no disponible"}',
                  style: typography.bodyMedium.copyWith(color: colors.accentTertiary),
                ),
                SizedBox(height: spacings.sm),
                if (exp.description.isNotEmpty)
                  Text(
                    exp.description,
                    style: typography.bodyMedium.copyWith(color: colors.textSecondary, height: 1.5),
                  ),
                if (exp.achievements.isNotEmpty) ...[
                  SizedBox(height: spacings.sm),
                  ...exp.achievements.map((ach) => Padding(
                    padding: const EdgeInsets.only(bottom: 4.0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('• ', style: typography.bodyMedium.copyWith(color: colors.accentPrimary)),
                        Expanded(child: Text(ach, style: typography.bodyMedium.copyWith(color: colors.textSecondary))),
                      ],
                    ),
                  )),
                ],
              ],
            ),
          ),
        ),
        ],
      ),
    );
  }
}
