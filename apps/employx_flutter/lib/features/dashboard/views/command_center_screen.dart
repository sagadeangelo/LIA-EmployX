import 'package:flutter/material.dart';
import '../../../core/theme/lia_theme.dart';


class CommandCenterScreen extends StatefulWidget {
  const CommandCenterScreen({Key? key}) : super(key: key);

  @override
  State<CommandCenterScreen> createState() => _CommandCenterScreenState();
}

class _CommandCenterScreenState extends State<CommandCenterScreen> with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  
  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final spacings = context.liaSpacings;

    return Scaffold(
      backgroundColor: colors.background,
      body: Stack(
        children: [
          // Background Gradient subtle
          Positioned(
            top: -200,
            right: -200,
            child: Container(
              width: 600,
              height: 600,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    const Color(0xFF10B981).withAlpha(15), // Emerald Career Agent color
                    colors.background.withAlpha(0),
                  ],
                ),
              ),
            ),
          ),
          
          Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  padding: EdgeInsets.symmetric(horizontal: spacings.xxxl, vertical: spacings.xxxl),
                  child: Center(
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 1000),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildGreeting(context),
                          SizedBox(height: spacings.xxxl),
                          
                          // Top Section: Live Report + Priorities
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                flex: 6,
                                child: _buildCareerExecutiveReport(context),
                              ),
                              SizedBox(width: spacings.xxl),
                              Expanded(
                                flex: 4,
                                child: Column(
                                  children: [
                                    _buildTodayPriorities(context),
                                    SizedBox(height: spacings.xl),
                                    _buildAgentInsights(context),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          
                          SizedBox(height: spacings.xxxl),
                          
                          // Middle Section: Professional Tools
                          _buildProfessionalTools(context),
                          
                          SizedBox(height: spacings.xxxl),
                          
                          // Bottom Section: Detected Opportunities
                          _buildDetectedOpportunities(context),
                          
                          const SizedBox(height: 100), // Padding for Command Bar
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              
              // Command Bar (Sticky Bottom)
              _buildCommandBar(context),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildGreeting(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Buenos días, Miguel.',
          style: typography.display.copyWith(color: colors.textPrimary, fontSize: 40),
        ),
        SizedBox(height: spacings.sm),
        Text(
          '¿Qué quieres lograr hoy?',
          style: typography.h2.copyWith(color: colors.textSecondary, fontWeight: FontWeight.normal),
        ),
      ],
    );
  }

  Widget _buildCareerExecutiveReport(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;
    final careerColor = const Color(0xFF10B981);

    return Container(
      padding: EdgeInsets.all(spacings.xl),
      decoration: BoxDecoration(
        color: colors.surface.withAlpha(128),
        borderRadius: spacings.radiusLg,
        border: Border.all(color: careerColor.withAlpha(50)),
        boxShadow: [
          BoxShadow(
            color: careerColor.withAlpha(10),
            blurRadius: 30,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              AnimatedBuilder(
                animation: _pulseController,
                builder: (context, child) {
                  return Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: careerColor,
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: careerColor.withAlpha((_pulseController.value * 128).toInt() + 50),
                          blurRadius: 10,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                  );
                },
              ),
              SizedBox(width: spacings.sm),
              Text('Career Agent IA', style: typography.h3.copyWith(color: careerColor)),
            ],
          ),
          SizedBox(height: spacings.lg),
          Text(
            'Anoche terminé de revisar tu perfil.\n\nEncontré 16 nuevas vacantes.\nDetecté que agregar Docker incrementaría tu ATS un 9%.\n\nMientras dormías también:\n✔ Revisé salarios\n✔ Actualicé tendencias\n✔ Analicé LinkedIn\n\n¿Qué hacemos ahora?',
            style: typography.bodyLarge.copyWith(color: colors.textPrimary, height: 1.6),
          ),
          SizedBox(height: spacings.xl),
          Wrap(
            spacing: spacings.sm,
            runSpacing: spacings.sm,
            children: [
              _buildQuickReportButton(context, 'Optimizar CV', Icons.auto_fix_high),
              _buildQuickReportButton(context, 'Buscar más empleos', Icons.search),
              _buildQuickReportButton(context, 'Aplicar automáticamente', Icons.send),
              _buildQuickReportButton(context, 'Preparar entrevista', Icons.mic),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickReportButton(BuildContext context, String text, IconData icon) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: colors.surfaceHover,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: colors.border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: colors.textSecondary),
          const SizedBox(width: 8),
          Text(text, style: typography.caption.copyWith(color: colors.textPrimary, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildTodayPriorities(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Container(
      padding: EdgeInsets.all(spacings.xl),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: spacings.radiusLg,
        border: Border.all(color: colors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Prioridades de hoy', style: typography.h3.copyWith(color: colors.textPrimary)),
          SizedBox(height: spacings.lg),
          _buildPriorityItem(context, 'Mejorar ATS', true),
          _buildPriorityItem(context, 'Aplicar a Microsoft', false),
          _buildPriorityItem(context, 'Actualizar LinkedIn', false),
          _buildPriorityItem(context, 'Practicar entrevista', false),
        ],
      ),
    );
  }

  Widget _buildPriorityItem(BuildContext context, String text, bool isDone) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Padding(
      padding: EdgeInsets.only(bottom: spacings.sm),
      child: Row(
        children: [
          Container(
            width: 20,
            height: 20,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: isDone ? const Color(0xFF10B981) : colors.border, width: 2),
              color: isDone ? const Color(0xFF10B981).withAlpha(50) : Colors.transparent,
            ),
            child: isDone ? const Icon(Icons.check, size: 12, color: Color(0xFF10B981)) : null,
          ),
          SizedBox(width: spacings.sm),
          Text(
            text,
            style: typography.bodyMedium.copyWith(
              color: isDone ? colors.textSecondary : colors.textPrimary,
              decoration: isDone ? TextDecoration.lineThrough : null,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentInsights(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Container(
      padding: EdgeInsets.all(spacings.lg),
      decoration: BoxDecoration(
        color: colors.accentPrimary.withAlpha(15),
        borderRadius: spacings.radiusLg,
        border: Border.all(color: colors.accentPrimary.withAlpha(50)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.insights, color: colors.accentPrimary),
          SizedBox(width: spacings.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Career Insight', style: typography.caption.copyWith(color: colors.accentPrimary, fontWeight: FontWeight.bold)),
                SizedBox(height: spacings.xs),
                Text(
                  'El mercado Flutter está aumentando un 18%. Te recomiendo priorizar empresas remotas.',
                  style: typography.bodyMedium.copyWith(color: colors.textPrimary),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProfessionalTools(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Herramientas Profesionales', style: typography.h3.copyWith(color: colors.textPrimary)),
        SizedBox(height: spacings.lg),
        Wrap(
          spacing: spacings.lg,
          runSpacing: spacings.lg,
          children: [
            _buildToolCard(context, 'Crear CV', 'Genera un CV profesional desde cero.', Icons.description),
            _buildToolCard(context, 'Analizar CV', 'Encuentra áreas de mejora en segundos.', Icons.analytics),
            _buildToolCard(context, 'Optimizar ATS', 'Ajusta palabras clave para pasar los filtros.', Icons.radar),
            _buildToolCard(context, 'Buscar Vacantes', 'Rastrea la web buscando tu perfil ideal.', Icons.work),
            _buildToolCard(context, 'Cover Letter', 'Cartas generadas específicamente por empresa.', Icons.draw),
            _buildToolCard(context, 'Entrevistas', 'Simulacros con feedback en tiempo real.', Icons.mic),
          ],
        ),
      ],
    );
  }

  Widget _buildToolCard(BuildContext context, String title, String desc, IconData icon) {
    return _HoverableToolCard(
      title: title,
      desc: desc,
      icon: icon,
    );
  }

  Widget _buildDetectedOpportunities(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Oportunidades Detectadas', style: typography.h3.copyWith(color: colors.textPrimary)),
        SizedBox(height: spacings.lg),
        Row(
          children: [
            Expanded(child: _buildOpportunityItem(context, 'Microsoft', 94, true)),
            SizedBox(width: spacings.lg),
            Expanded(child: _buildOpportunityItem(context, 'Amazon', 91, false)),
            SizedBox(width: spacings.lg),
            Expanded(child: _buildOpportunityItem(context, 'Google', 89, false)),
            SizedBox(width: spacings.lg),
            Expanded(child: _buildOpportunityItem(context, 'Oracle', 87, false)),
          ],
        ),
      ],
    );
  }

  Widget _buildOpportunityItem(BuildContext context, String company, int match, bool isHot) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Container(
      padding: EdgeInsets.all(spacings.lg),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: spacings.radiusLg,
        border: Border.all(color: isHot ? const Color(0xFFF59E0B).withAlpha(100) : colors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  if (isHot) const Text('🔥 '),
                  Text(company, style: typography.h3.copyWith(color: colors.textPrimary, fontSize: 16)),
                ],
              ),
              Text('$match%', style: typography.caption.copyWith(color: isHot ? const Color(0xFFF59E0B) : colors.textSecondary, fontWeight: FontWeight.bold)),
            ],
          ),
          SizedBox(height: spacings.md),
          // Mini Match Bar
          Container(
            height: 4,
            decoration: BoxDecoration(
              color: colors.surfaceHover,
              borderRadius: BorderRadius.circular(2),
            ),
            child: FractionallySizedBox(
              widthFactor: match / 100,
              child: Container(
                decoration: BoxDecoration(
                  color: isHot ? const Color(0xFFF59E0B) : colors.textSecondary,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCommandBar(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return Positioned(
      bottom: spacings.xxl,
      left: MediaQuery.of(context).size.width / 2 - 350,
      width: 700,
      child: Container(
        height: 56,
        padding: EdgeInsets.symmetric(horizontal: spacings.lg),
        decoration: BoxDecoration(
          color: colors.surface.withAlpha(230),
          borderRadius: BorderRadius.circular(28),
          border: Border.all(color: colors.border.withAlpha(100)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withAlpha(100),
              blurRadius: 30,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Row(
          children: [
            Icon(Icons.auto_awesome, color: colors.accentPrimary, size: 20),
            SizedBox(width: spacings.md),
            Expanded(
              child: Text(
                'Pregunta algo...',
                style: typography.bodyLarge.copyWith(color: colors.textSecondary),
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: colors.surfaceHover,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: colors.border),
              ),
              child: Text('⌘ K', style: typography.caption.copyWith(color: colors.textSecondary, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }
}

class _HoverableToolCard extends StatefulWidget {
  final String title;
  final String desc;
  final IconData icon;

  const _HoverableToolCard({required this.title, required this.desc, required this.icon});

  @override
  State<_HoverableToolCard> createState() => _HoverableToolCardState();
}

class _HoverableToolCardState extends State<_HoverableToolCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    final colors = context.liaColors;
    final typography = context.liaTypography;
    final spacings = context.liaSpacings;

    return MouseRegion(
      onEnter: (_) => setState(() => _isHovered = true),
      onExit: (_) => setState(() => _isHovered = false),
      cursor: SystemMouseCursors.click,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 300,
        padding: EdgeInsets.all(spacings.lg),
        decoration: BoxDecoration(
          color: _isHovered ? colors.surfaceHover : colors.surface,
          borderRadius: spacings.radiusLg,
          border: Border.all(color: _isHovered ? colors.border.withAlpha(128) : colors.border.withAlpha(50)),
          boxShadow: [
            if (_isHovered)
              BoxShadow(
                color: Colors.black.withAlpha(50),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(widget.icon, color: colors.textPrimary, size: 20),
                SizedBox(width: spacings.sm),
                Text(widget.title, style: typography.bodyLarge.copyWith(color: colors.textPrimary, fontWeight: FontWeight.bold)),
              ],
            ),
            Padding(
              padding: EdgeInsets.symmetric(vertical: spacings.md),
              child: Divider(color: colors.border),
            ),
            Text(
              widget.desc,
              style: typography.bodyMedium.copyWith(color: colors.textSecondary, height: 1.4),
            ),
            SizedBox(height: spacings.lg),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                Icon(Icons.play_arrow, size: 14, color: _isHovered ? colors.accentPrimary : colors.textMuted),
                SizedBox(width: 4),
                Text('Abrir', style: typography.caption.copyWith(color: _isHovered ? colors.accentPrimary : colors.textMuted, fontWeight: FontWeight.bold)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
