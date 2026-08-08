import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/lia_theme.dart';
import '../../../core/actions/mission_actions.dart';

class ProfessionalGoalScreen extends StatelessWidget {
  const ProfessionalGoalScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    
    final missionActions = context.watch<MissionActions>();
    final mission = missionActions.currentMission;

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
          
          if (missionActions.isLoading && mission == null)
            const Center(child: CircularProgressIndicator())
          else if (mission == null)
            Center(
              child: Text(
                'No hay Misión Activa. Configura una nueva misión.',
                style: typography.h2.copyWith(color: colors.textSecondary),
              ),
            )
          else
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
                        mission.title,
                        style: typography.h2.copyWith(color: colors.textSecondary),
                      ),
                      SizedBox(height: spacings.md),
                      Text(
                        mission.careerGoal,
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
                          _buildSpecCard(context, Icons.business, 'Empresa ideal', (mission.configuration['target_company'] as String?) ?? 'Abierto'),
                          _buildSpecCard(context, Icons.attach_money, 'Meta salarial', mission.configuration['salary_goal'] != null ? '\$${mission.configuration['salary_goal']}' : 'Por definir'),
                          _buildSpecCard(context, Icons.computer, 'Modalidad', (mission.configuration['remote'] as bool? ?? false) ? 'Remoto' : 'Presencial/Híbrido'),
                          _buildSpecCard(context, Icons.public, 'Ubicación', (mission.configuration['location'] as String?) ?? 'Flexible'),
                          _buildSpecCard(context, Icons.work, 'Posición', (mission.configuration['target_position'] as String?) ?? 'Cualquiera'),
                          _buildSpecCard(context, Icons.timer, 'Fecha objetivo', mission.configuration['deadline'] != null ? mission.configuration['deadline'].toString().split(' ')[0] : 'Abierto'),
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
                                    'Tus agentes (${mission.activeAgents.join(', ')}) están calibrados y optimizando continuamente sus estrategias para cumplir esta misión (Misión ID: ${mission.id}).',
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
