import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';
import '../../../core/ui/lia_card.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({Key? key}) : super(key: key);

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
              'Dashboard',
              style: typography.h2.copyWith(color: colors.textPrimary),
            ),
            SizedBox(height: spacings.sm),
            Text(
              'Tu progreso y métricas recientes.',
              style: typography.bodyMedium.copyWith(color: colors.textSecondary),
            ),
            SizedBox(height: spacings.xl),
            
            // Stats Grid
            GridView.count(
              crossAxisCount: 3,
              crossAxisSpacing: spacings.md,
              mainAxisSpacing: spacings.md,
              shrinkWrap: true,
              childAspectRatio: 1.5,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildStatCard(context, 'Postulaciones', '12', Icons.send_outlined),
                _buildStatCard(context, 'Match Promedio', '85%', Icons.analytics_outlined),
                _buildStatCard(context, 'Entrevistas', '2', Icons.calendar_today_outlined),
              ],
            ),
            
            SizedBox(height: spacings.xl),
            
            Text(
              'Actividad Reciente',
              style: typography.h3.copyWith(color: colors.textPrimary),
            ),
            SizedBox(height: spacings.md),
            
            // Recent Activity List
            LiaCard(
              child: Column(
                children: [
                  _buildActivityItem(context, 'Subiste un nuevo CV "Perfil Backend"'),
                  Divider(color: colors.border),
                  _buildActivityItem(context, 'IA analizó tu CV: 3 sugerencias de mejora'),
                  Divider(color: colors.border),
                  _buildActivityItem(context, 'Guardaste la vacante "Senior Flutter Developer"'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(BuildContext context, String title, String value, IconData icon) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return LiaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            children: [
              Icon(icon, color: colors.textSecondary, size: 20),
              SizedBox(width: spacings.xs),
              Text(title, style: typography.bodyMedium.copyWith(color: colors.textSecondary)),
            ],
          ),
          SizedBox(height: spacings.sm),
          Text(value, style: typography.h1.copyWith(color: colors.textPrimary)),
        ],
      ),
    );
  }

  Widget _buildActivityItem(BuildContext context, String text) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Padding(
      padding: EdgeInsets.symmetric(vertical: spacings.sm),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: colors.accentPrimary,
              shape: BoxShape.circle,
            ),
          ),
          SizedBox(width: spacings.md),
          Text(text, style: typography.bodyMedium.copyWith(color: colors.textPrimary)),
        ],
      ),
    );
  }
}
