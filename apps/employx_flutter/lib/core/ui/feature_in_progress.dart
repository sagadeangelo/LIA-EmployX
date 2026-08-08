import 'package:flutter/material.dart';
import '../theme/lia_theme.dart';

class FeatureInProgressWidget extends StatelessWidget {
  final String featureName;

  const FeatureInProgressWidget({Key? key, required this.featureName}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Center(
      child: Container(
        padding: EdgeInsets.all(spacings.xxxl),
        decoration: BoxDecoration(
          color: colors.surface,
          borderRadius: spacings.radiusLg,
          border: Border.all(color: colors.border),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.construction, size: 64, color: colors.accentPrimary),
            SizedBox(height: spacings.xl),
            Text(
              'En Desarrollo',
              style: typography.h2.copyWith(color: colors.textPrimary),
            ),
            SizedBox(height: spacings.md),
            Text(
              'La pantalla "$featureName" está siendo conectada al ecosistema de Agentes.\nPronto estará disponible.',
              textAlign: TextAlign.center,
              style: typography.bodyLarge.copyWith(color: colors.textSecondary),
            ),
          ],
        ),
      ),
    );
  }
}
