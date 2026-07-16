import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_button.dart';
import '../../../core/ui/lia_card.dart';

class MyCvsScreen extends StatelessWidget {
  const MyCvsScreen({Key? key}) : super(key: key);

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
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Mis CVs',
                      style: typography.h2.copyWith(color: colors.textPrimary),
                    ),
                    SizedBox(height: spacings.xs),
                    Text(
                      'Gestiona tus diferentes perfiles profesionales.',
                      style: typography.bodyMedium.copyWith(color: colors.textSecondary),
                    ),
                  ],
                ),
                LiaButton(
                  text: 'Nuevo CV',
                  icon: Icons.add,
                  onPressed: () {},
                ),
              ],
            ),
            SizedBox(height: spacings.xxl),
            
            // Grid of CVs
            GridView.count(
              crossAxisCount: 3,
              crossAxisSpacing: spacings.lg,
              mainAxisSpacing: spacings.lg,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildCvCard(context, 'Perfil Flutter Senior', 'Actualizado hace 2 días', true),
                _buildCvCard(context, 'Perfil Backend Python', 'Actualizado hace 1 mes', false),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCvCard(BuildContext context, String title, String subtitle, bool isDefault) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaCard(
      isHoverable: true,
      onTap: () {},
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(Icons.description_outlined, color: colors.textSecondary, size: 24),
              if (isDefault)
                Icon(Icons.star, color: colors.accentPrimary, size: 16),
            ],
          ),
          Spacer(),
          Text(title, style: typography.h3.copyWith(color: colors.textPrimary)),
          SizedBox(height: spacings.xs),
          Text(subtitle, style: typography.caption.copyWith(color: colors.textMuted)),
        ],
      ),
    );
  }
}
