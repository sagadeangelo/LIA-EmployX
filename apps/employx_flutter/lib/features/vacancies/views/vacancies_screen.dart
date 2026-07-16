import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_card.dart';
import '../../../core/ui/lia_chip.dart';

class VacanciesScreen extends StatelessWidget {
  const VacanciesScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: SingleChildScrollView(
        padding: EdgeInsets.all(spacings.xl),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Vacantes',
              style: typography.h2.copyWith(color: colors.textPrimary),
            ),
            SizedBox(height: spacings.xs),
            Text(
              'Explora y gestiona oportunidades laborales.',
              style: typography.bodyMedium.copyWith(color: colors.textSecondary),
            ),
            SizedBox(height: spacings.xxl),
            
            // Vacancies List
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: 3,
              separatorBuilder: (_, __) => SizedBox(height: spacings.md),
              itemBuilder: (context, index) {
                return _buildVacancyCard(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVacancyCard(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaCard(
      isHoverable: true,
      onTap: () {},
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Company Logo Placeholder
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: colors.surfaceHover,
              borderRadius: spacings.radiusSm,
            ),
            child: Icon(Icons.business, color: colors.textSecondary),
          ),
          SizedBox(width: spacings.md),
          
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Senior Flutter Developer', style: typography.h3.copyWith(color: colors.textPrimary)),
                SizedBox(height: spacings.xxs),
                Text('TechCorp Inc. • Madrid, España (Híbrido)', style: typography.bodyMedium.copyWith(color: colors.textSecondary)),
                SizedBox(height: spacings.md),
                Wrap(
                  spacing: spacings.xs,
                  runSpacing: spacings.xs,
                  children: [
                    LiaChip(label: 'Flutter'),
                    LiaChip(label: 'Dart'),
                    LiaChip(label: 'Clean Architecture'),
                  ],
                ),
              ],
            ),
          ),
          
          // Match Score
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('92%', style: typography.h2.copyWith(color: colors.accentSecondary)),
              Text('Match', style: typography.caption.copyWith(color: colors.textMuted)),
            ],
          )
        ],
      ),
    );
  }
}
