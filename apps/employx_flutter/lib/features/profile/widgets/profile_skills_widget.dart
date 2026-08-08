import 'package:flutter/material.dart';
import '../../../../core/theme/lia_theme.dart';
import '../../../../core/models/professional_profile_model.dart';
import '../../../../core/ui/lia_glass_panel.dart';

class ProfileSkillsWidget extends StatelessWidget {
  final ProfessionalProfile profile;

  const ProfileSkillsWidget({Key? key, required this.profile}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    final technicalSkills = profile.skills.technicalSkills;
    final softSkills = profile.skills.softSkills;

    if (technicalSkills.isEmpty && softSkills.isEmpty) return const SizedBox.shrink();

    return LiaGlassPanel(
      padding: EdgeInsets.all(spacings.xl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.psychology_outlined, color: colors.accentPrimary, size: 24),
              SizedBox(width: spacings.sm),
              Text('Habilidades (Skills)', style: typography.h3.copyWith(color: colors.textPrimary)),
            ],
          ),
          SizedBox(height: spacings.lg),
          if (technicalSkills.isNotEmpty) ...[
            Text('Technical Skills', style: typography.caption.copyWith(color: colors.textMuted)),
            SizedBox(height: spacings.sm),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: technicalSkills.map((s) => _buildChip(context, s, isTechnical: true)).toList(),
            ),
            SizedBox(height: spacings.lg),
          ],
          if (softSkills.isNotEmpty) ...[
            Text('Soft Skills', style: typography.caption.copyWith(color: colors.textMuted)),
            SizedBox(height: spacings.sm),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: softSkills.map((s) => _buildChip(context, s, isTechnical: false)).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildChip(BuildContext context, String label, {required bool isTechnical}) {
    final colors = context.liaColors;
    final typography = context.liaTypography;

    final bgColor = isTechnical 
        ? colors.accentPrimary.withValues(alpha: 0.1) 
        : colors.accentTertiary.withValues(alpha: 0.1);
    
    final textColor = isTechnical 
        ? colors.accentPrimary 
        : colors.accentTertiary;

    final borderColor = isTechnical
        ? colors.accentPrimary.withValues(alpha: 0.3)
        : colors.accentTertiary.withValues(alpha: 0.3);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
      ),
      child: Text(
        label,
        style: typography.bodyMedium.copyWith(color: textColor, fontWeight: FontWeight.w500),
      ),
    );
  }
}
