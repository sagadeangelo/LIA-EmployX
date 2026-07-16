import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';

class ProfessionalGoalScreen extends StatelessWidget {
  const ProfessionalGoalScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: Stack(
        children: [
          // Ambient Glow
          Positioned(
            top: -100,
            left: MediaQuery.of(context).size.width / 2 - 300,
            child: Container(
              width: 600,
              height: 400,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    colors.accentPrimary.withAlpha(40),
                    colors.background.withAlpha(0),
                  ],
                ),
              ),
            ),
          ),
          
          SingleChildScrollView(
            padding: EdgeInsets.symmetric(horizontal: spacings.xxxl, vertical: spacings.xxxl),
            child: Center(
              child: Container(
                constraints: const BoxConstraints(maxWidth: 800),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    // Header
                    Container(
                      padding: EdgeInsets.symmetric(horizontal: spacings.md, vertical: spacings.xs),
                      decoration: BoxDecoration(
                        color: colors.surfaceHover,
                        borderRadius: BorderRadius.circular(100),
                        border: Border.all(color: colors.border),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.flag, size: 16, color: colors.accentPrimary),
                          SizedBox(width: spacings.sm),
                          Text(
                            'DIRECTRIZ PRINCIPAL',
                            style: typography.caption.copyWith(
                              color: colors.accentPrimary,
                              letterSpacing: 2,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    SizedBox(height: spacings.xl),
                    
                    Text(
                      'Mi Objetivo',
                      style: typography.h2.copyWith(color: colors.textSecondary),
                    ),
                    SizedBox(height: spacings.md),
                    Text(
                      'Conseguir empleo Flutter Senior',
                      style: typography.display.copyWith(
                        color: colors.textPrimary,
                        fontSize: 48,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    
                    SizedBox(height: spacings.xl),
                    
                    // Divider Line
                    Container(
                      height: 1,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            colors.border.withAlpha(0),
                            colors.border,
                            colors.border.withAlpha(0),
                          ],
                        ),
                      ),
                    ),
                    
                    SizedBox(height: spacings.xxxl),
                    
                    // Specs Grid
                    Wrap(
                      spacing: spacings.xl,
                      runSpacing: spacings.xl,
                      alignment: WrapAlignment.center,
                      children: [
                        _buildSpecCard(context, Icons.business, 'Empresa ideal', 'Microsoft'),
                        _buildSpecCard(context, Icons.attach_money, 'Meta salarial', '\$120,000 MXN'),
                        _buildSpecCard(context, Icons.computer, 'Modalidad', 'Remoto'),
                        _buildSpecCard(context, Icons.public, 'País', 'USA'),
                        _buildSpecCard(context, Icons.language, 'Idioma', 'English'),
                        _buildSpecCard(context, Icons.timer, 'Fecha objetivo', '90 días'),
                      ],
                    ),
                    
                    SizedBox(height: spacings.xxxl),
                    
                    // The "Why" statement
                    Container(
                      padding: EdgeInsets.all(spacings.xl),
                      decoration: BoxDecoration(
                        color: colors.surface.withAlpha(128), // Glass
                        borderRadius: spacings.radiusLg,
                        border: Border.all(color: colors.border),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withAlpha(50),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: EdgeInsets.all(spacings.md),
                            decoration: BoxDecoration(
                              color: colors.surfaceHover,
                              shape: BoxShape.circle,
                            ),
                            child: Icon(Icons.info_outline, color: colors.textSecondary),
                          ),
                          SizedBox(width: spacings.xl),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'Sincronización del Sistema',
                                  style: typography.h3.copyWith(color: colors.textPrimary),
                                ),
                                SizedBox(height: spacings.xs),
                                Text(
                                  'Todos tus Agentes IA instalados están calibrados y optimizando continuamente sus estrategias para cumplir este objetivo exacto.',
                                  style: typography.bodyMedium.copyWith(color: colors.textSecondary),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSpecCard(BuildContext context, IconData icon, String label, String value) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    
    return Container(
      width: 240,
      padding: EdgeInsets.all(spacings.xl),
      decoration: BoxDecoration(
        color: colors.surface.withAlpha(128),
        borderRadius: spacings.radiusLg,
        border: Border.all(color: colors.border.withAlpha(128)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: colors.textSecondary, size: 24),
          SizedBox(height: spacings.lg),
          Text(
            label,
            style: typography.caption.copyWith(color: colors.textSecondary),
          ),
          SizedBox(height: spacings.xs),
          Text(
            value,
            style: typography.h3.copyWith(color: colors.textPrimary),
          ),
        ],
      ),
    );
  }
}
